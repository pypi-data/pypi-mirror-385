"""OpenAI Batch API client for CVE enrichment with security context analysis."""

import json
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from openai import OpenAI
from pydantic import ValidationError

from ..core.logging import get_logger
from .models import SimpleCVEEnrichment

logger = get_logger(__name__)


class OpenAIEnricher:
    """OpenAI Batch API-based CVE enrichment engine.

    Uses OpenAI Batch API to analyze CVEs asynchronously in the context of UDS Core
    security controls (NetworkPolicies and Pepr admission policies) to generate
    mitigation strategies.

    The Batch API provides 50% cost savings compared to synchronous API calls.

    Attributes:
        client: OpenAI client instance
        model: OpenAI model to use (e.g., "gpt-5-nano", "gpt-5-mini")
        temperature: Fixed at 1.0 (required by gpt-5 models)
        baseline_context: Baseline security context from UDS Core
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-5-nano",
        reasoning_effort: str = "medium",
        verbosity: str = "medium",
        max_completion_tokens: int | None = None,
        seed: int | None = None,
        metadata: dict[str, str] | None = None,
        baseline_context_path: Path | None = None,
    ):
        """Initialize OpenAI Batch API enricher.

        Args:
            api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-5-nano)
            reasoning_effort: Reasoning effort level (minimal, low, medium, high) (default: medium)
            verbosity: Verbosity level for model responses (low, medium, high) (default: medium)
            max_completion_tokens: Optional upper bound for total tokens including reasoning tokens
            seed: Optional seed for reproducible results
            metadata: Optional metadata tags for OpenAI requests
            baseline_context_path: Path to baseline security context markdown file
                                   If None, uses default from package

        Note:
            Temperature is fixed at 1.0 as required by gpt-5 models.
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = 1.0
        self.reasoning_effort = reasoning_effort
        self.verbosity = verbosity
        self.max_completion_tokens = max_completion_tokens
        self.seed = seed
        self.metadata = metadata

        # Validate model is available
        self._validate_model()

        self.baseline_context = self._load_baseline_context(baseline_context_path)
        self.system_prompt = self._build_system_prompt()
        logger.info(
            "OpenAI Batch API enricher initialized",
            model=model,
            temperature=self.temperature,
            reasoning_effort=self.reasoning_effort,
            verbosity=self.verbosity,
            max_completion_tokens=self.max_completion_tokens,
            seed=self.seed,
        )

    def _load_baseline_context(self, path: Path | None = None) -> str:
        """Load baseline security context from markdown file.

        Args:
            path: Optional custom path to baseline context file

        Returns:
            Baseline security context as string

        Raises:
            FileNotFoundError: If baseline context file not found
        """
        if path is None:
            # Use default baseline context from package
            path = Path(__file__).parent / "baseline_security_context.md"

        if not path.exists():
            raise FileNotFoundError(f"Baseline context file not found: {path}")

        logger.debug("Loading baseline security context", path=str(path))
        return path.read_text()

    def _validate_model(self) -> None:
        """Validate that the configured model is available via OpenAI API.

        Raises:
            ValueError: If model is not available or API call fails
        """
        try:
            logger.debug("Validating model availability", model=self.model)

            # List all available models from OpenAI
            models = self.client.models.list()

            # Extract model IDs
            available_model_ids = [model.id for model in models.data]

            # Check if configured model is in the list
            if self.model not in available_model_ids:
                logger.error(
                    "Model not available",
                    requested_model=self.model,
                    available_models=available_model_ids[:10],  # Show first 10 for brevity
                )
                raise ValueError(
                    f"Model '{self.model}' is not available. "
                    f"Available models include: {', '.join(available_model_ids[:10])}"
                )

            logger.debug("Model validation successful", model=self.model)

        except Exception as e:
            if isinstance(e, ValueError):
                raise
            logger.error("Failed to validate model", error=str(e), model=self.model)
            raise ValueError(f"Failed to validate model '{self.model}': {str(e)}") from e

    def _build_system_prompt(self) -> str:
        """Build system prompt with baseline security context.

        Returns:
            System prompt for OpenAI
        """
        return f"""You are a cybersecurity expert analyzing Common Vulnerabilities and Exposures (CVEs) \
in the context of a Kubernetes cluster running UDS Core.

UDS Core provides defense-in-depth security through:
- NetworkPolicies enforcing zero-trust networking
- Pepr admission policies preventing insecure configurations
- Istio service mesh providing mTLS and traffic control

Your task is to provide:
1. A 2 sentence explanation of how UDS Core helps mitigate the CVE
2. A 1 sentence impact analysis of what could happen WITHOUT UDS Core controls

Mitigation Format: "UDS helps to mitigate {{CVE_ID}} by {{explanation}}"

The mitigation explanation should:
- Be exactly ONE sentence
- Identify the most relevant security control(s)
- Focus on the primary mitigation mechanism

The impact analysis should:
- Be 1 sentences describing potential consequences without UDS Core
- Cover attack scenarios, data risks, and potential blast radius
- Be specific to this CVE's attack vector and severity

Baseline Security Context:
{self.baseline_context}

Respond ONLY with valid JSON matching the SimpleCVEEnrichment schema. Do not include markdown \
formatting, code blocks, or any text outside the JSON object."""

    def _build_user_prompt(self, cve_id: str, cve_data: dict[str, Any]) -> str:
        """Build user prompt for CVE analysis.

        Args:
            cve_id: CVE identifier (e.g., CVE-2025-8869)
            cve_data: Vulnerability data from unified report

        Returns:
            User prompt for OpenAI
        """
        severity = cve_data.get("severity", "UNKNOWN")
        description = cve_data.get("description", "No description available")

        # Extract CVSS scores if available
        cvss_info = ""
        if "cvss" in cve_data:
            cvss_data = cve_data["cvss"]
            if isinstance(cvss_data, list):
                for entry in cvss_data:
                    if entry.get("version", "").startswith("3"):
                        score = entry.get("metrics", {}).get("baseScore")
                        if score:
                            cvss_info += f"\nCVSS 3.x Base Score: {score}"

        # Extract fix information if available
        fix_info = ""
        if "fix" in cve_data and "versions" in cve_data["fix"]:
            versions = cve_data["fix"]["versions"]
            if versions:
                fix_info = f"\nFixed in versions: {', '.join(versions)}"

        timestamp = datetime.now(UTC).isoformat()

        prompt = f"""Analyze the following CVE in the context of UDS Core security controls:

CVE ID: {cve_id}
Severity: {severity}{cvss_info}
Description: {description}{fix_info}

Provide your analysis in JSON format with TWO key fields:

{{
  "cve_id": "{cve_id}",
  "mitigation_summary": "UDS helps to mitigate {cve_id} by [your single-sentence explanation here]",
  "impact_analysis": "[1 sentence explanation of potential impact without UDS Core controls]",
  "analysis_model": "{self.model}",
  "analysis_timestamp": "{timestamp}"
}}

Requirements for the mitigation_summary:
- MUST be exactly ONE sentence
- MUST start with "UDS helps to mitigate {cve_id} by"
- MUST identify the most relevant UDS Core security control(s)
- MUST be concise and specific
- Focus on NetworkPolicies, Pepr policies, or Istio service mesh controls

Requirements for the impact_analysis:
- MUST be 2 sentences in length
- Describe what could happen WITHOUT UDS Core controls in place
- Cover attack scenarios (e.g., remote code execution, privilege escalation)
- Describe potential data risks (e.g., exfiltration, tampering)
- Mention blast radius (e.g., lateral movement, cluster-wide compromise)
- Be specific to this CVE's severity and attack vector

Example:
{{
  "cve_id": "CVE-2024-12345",
  "mitigation_summary": "UDS helps to mitigate CVE-2024-12345 by enforcing non-root container execution \
through Pepr admission policies and blocking unauthorized external network access via default-deny NetworkPolicies.",
  "impact_analysis": "Without UDS Core controls, this critical vulnerability could allow an attacker to \
achieve remote code execution on the vulnerable container with root privileges. This could enable lateral \
movement across the cluster, exfiltration of sensitive data from connected services, and deployment of \
malicious workloads. The blast radius would extend beyond the compromised pod to potentially affect the entire \
cluster and connected infrastructure.",
  "analysis_model": "{self.model}",
  "analysis_timestamp": "{timestamp}"
}}
"""

        return prompt

    def _create_batch_request(self, cve_id: str, cve_data: dict[str, Any], custom_id: str) -> dict[str, Any]:
        """Create a single batch request for a CVE.

        Args:
            cve_id: CVE identifier (e.g., CVE-2025-8869)
            cve_data: Vulnerability data from unified report
            custom_id: Custom identifier for this request

        Returns:
            Batch request dictionary in JSONL format
        """
        # Build request body with required parameters
        body: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self._build_user_prompt(cve_id, cve_data)},
            ],
            "temperature": self.temperature,
            "reasoning_effort": self.reasoning_effort,
            "verbosity": self.verbosity,
            "response_format": {"type": "json_object"},
        }

        # Add optional parameters if provided
        if self.max_completion_tokens is not None:
            body["max_completion_tokens"] = self.max_completion_tokens
        if self.seed is not None:
            body["seed"] = self.seed

        # Metadata requires store to be enabled
        if self.metadata is not None:
            body["metadata"] = self.metadata
            body["store"] = True  # Required for metadata parameter

        return {
            "custom_id": custom_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": body,
        }

    def enrich_report(
        self,
        vulnerabilities: list[dict[str, Any]],
        max_cves: int | None = None,
        severity_filter: list[str] | None = None,
    ) -> dict[str, SimpleCVEEnrichment]:
        """Enrich multiple CVEs from a vulnerability report using OpenAI Batch API.

        This method submits CVEs to the Batch API and waits for completion.

        Args:
            vulnerabilities: List of vulnerability dictionaries
            max_cves: Maximum number of CVEs to enrich (None = all)
            severity_filter: List of severity levels to enrich (e.g., ["Critical", "High"])
                           If None, enriches all severities. Default: ["Critical", "High"]

        Returns:
            Dictionary mapping CVE IDs to SimpleCVEEnrichment objects
        """
        # Default to Critical and High if no filter specified
        if severity_filter is None:
            severity_filter = ["Critical", "High"]

        # Filter CVEs by severity and collect CVE data
        # Each tuple is (cve_id, vulnerability_data)
        cves_to_enrich: list[tuple[str, dict[str, Any]]] = []
        skipped_by_severity = 0

        for vuln in vulnerabilities:
            if max_cves and len(cves_to_enrich) >= max_cves:
                logger.info("Reached max CVE limit", max_cves=max_cves, collected=len(cves_to_enrich))
                break

            cve_id = vuln.get("vulnerability_id")
            if not cve_id:
                logger.warning("Skipping vulnerability without ID", vuln=vuln.get("count"))
                continue

            # Use vulnerability object for enrichment
            cve_data = vuln.get("vulnerability", {})

            # Apply severity filter
            severity = cve_data.get("severity", "Unknown")
            if severity_filter and severity not in severity_filter:
                logger.debug(
                    "Skipping CVE due to severity filter",
                    cve_id=cve_id,
                    severity=severity,
                    allowed_severities=severity_filter,
                )
                skipped_by_severity += 1
                continue

            cves_to_enrich.append((cve_id, cve_data))

        if not cves_to_enrich:
            logger.info("No CVEs to enrich after filtering")
            return {}

        logger.info(
            "Starting Batch API CVE enrichment",
            total_vulnerabilities=len(vulnerabilities),
            cves_to_enrich=len(cves_to_enrich),
            skipped_by_severity=skipped_by_severity,
            severity_filter=severity_filter,
        )

        # Create batch requests
        batch_requests = []
        for idx, (cve_id, cve_data) in enumerate(cves_to_enrich):
            custom_id = f"cve-{idx}-{cve_id}"
            batch_requests.append(self._create_batch_request(cve_id, cve_data, custom_id))

        # Write batch requests to JSONL file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            batch_file_path = Path(f.name)
            for request in batch_requests:
                f.write(json.dumps(request) + "\n")

        logger.info("Created batch request file", path=str(batch_file_path), requests=len(batch_requests))

        # Log first request for debugging
        if batch_requests:
            logger.debug("Sample batch request", request=batch_requests[0])

        try:
            # Upload batch input file
            logger.info("Uploading batch file to OpenAI")
            with open(batch_file_path, "rb") as f:
                batch_input_file = self.client.files.create(file=f, purpose="batch")

            logger.info("Batch file uploaded", file_id=batch_input_file.id)

            # Create batch
            logger.info("Creating batch job")
            batch = self.client.batches.create(
                input_file_id=batch_input_file.id,
                endpoint="/v1/chat/completions",
                completion_window="24h",
                metadata={"description": "CVE enrichment batch"},
            )

            logger.info(
                "Batch job created",
                batch_id=batch.id,
                status=batch.status,
                request_counts=batch.request_counts,
            )

            # Poll for completion
            logger.info("Waiting for batch completion (polling every 10 seconds)")
            while batch.status in ["validating", "in_progress", "finalizing"]:
                time.sleep(10)
                batch = self.client.batches.retrieve(batch.id)
                logger.info(
                    "Batch status update",
                    batch_id=batch.id,
                    status=batch.status,
                    request_counts=batch.request_counts,
                )

            if batch.status == "failed":
                logger.error("Batch job failed", batch_id=batch.id, errors=batch.errors)
                return {}

            if batch.status == "expired":
                logger.error("Batch job expired", batch_id=batch.id)
                return {}

            if batch.status == "cancelled":
                logger.error("Batch job cancelled", batch_id=batch.id)
                return {}

            # Download results
            logger.info("Batch completed, downloading results", output_file_id=batch.output_file_id)

            # Check for error file if no output (all requests failed)
            if not batch.output_file_id:
                logger.error("No output file ID in completed batch - all requests may have failed")

                # Try to get error details from error file
                if batch.error_file_id:
                    logger.info("Downloading error file for details", error_file_id=batch.error_file_id)
                    try:
                        error_content = self.client.files.content(batch.error_file_id)
                        error_data = error_content.read().decode("utf-8")

                        # Parse first few errors to understand what went wrong
                        error_lines = error_data.strip().split("\n")[:3]  # Show first 3 errors
                        for line in error_lines:
                            error_result = json.loads(line)
                            logger.error(
                                "Batch request error",
                                custom_id=error_result.get("custom_id"),
                                error=error_result.get("error"),
                            )
                    except Exception as e:
                        logger.error("Failed to download error file", error=str(e))

                return {}

            output_content = self.client.files.content(batch.output_file_id)
            output_data = output_content.read().decode("utf-8")

            # Parse results
            enrichments: dict[str, SimpleCVEEnrichment] = {}
            for line in output_data.strip().split("\n"):
                result = json.loads(line)
                custom_id = result["custom_id"]

                if result.get("error"):
                    logger.error("Request failed", custom_id=custom_id, error=result["error"])
                    continue

                response = result["response"]
                content = response["body"]["choices"][0]["message"]["content"]

                try:
                    enrichment_data = json.loads(content)
                    enrichment = SimpleCVEEnrichment(**enrichment_data)
                    enrichments[enrichment.cve_id] = enrichment
                    logger.debug("CVE enrichment successful", cve_id=enrichment.cve_id)
                except (json.JSONDecodeError, ValidationError) as e:
                    logger.error(
                        "Failed to parse enrichment response",
                        custom_id=custom_id,
                        error=str(e),
                        content=content[:200],
                    )

            logger.info(
                "CVE enrichment complete",
                total_vulnerabilities=len(vulnerabilities),
                cves_to_enrich=len(cves_to_enrich),
                successful_enrichments=len(enrichments),
                skipped_by_severity=skipped_by_severity,
                severity_filter=severity_filter,
            )

            return enrichments

        finally:
            # Cleanup temporary file
            if batch_file_path.exists():
                batch_file_path.unlink()
                logger.debug("Cleaned up temporary batch file")
