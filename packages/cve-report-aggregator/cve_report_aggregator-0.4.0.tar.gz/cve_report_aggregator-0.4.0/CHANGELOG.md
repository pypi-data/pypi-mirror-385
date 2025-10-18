# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0](https://github.com/mkm29/cve-report-aggregator/compare/v0.3.0...v0.4.0) (2025-10-18)


### Features

* Add Docker build trigger after successful release ([dfcf8f2](https://github.com/mkm29/cve-report-aggregator/commit/dfcf8f21b801bc3d6d51b713acdd612adbb7a576))
* Add Docker build trigger after successful release ([c8bc662](https://github.com/mkm29/cve-report-aggregator/commit/c8bc66269dd7ae870633c212685bc1d05872dc6d))

## [0.3.0](https://github.com/mkm29/cve-report-aggregator/compare/v0.2.0...v0.3.0) (2025-10-18)


### Features

* Implement comprehensive configuration management using Pydantic Settings with YAML support ([4d62a3f](https://github.com/mkm29/cve-report-aggregator/commit/4d62a3fa19cb8713e17ddf37c6b8c0a59fcb50f7))
* implement pydantic app config and mkdocs site ([f699282](https://github.com/mkm29/cve-report-aggregator/commit/f6992826f79c91c5c424d1b8cef57cfb7ca65408))
* pydantic config and mkdocs site ([ff707ed](https://github.com/mkm29/cve-report-aggregator/commit/ff707eddf87de2612163dcc053e5a424f7af4974))


### Bug Fixes

* Update documentation links and improve .gitignore configuration ([ab0324e](https://github.com/mkm29/cve-report-aggregator/commit/ab0324e285d057376eeab69f2886dfc61934dc24))
* Update documentation links and improve .gitignore configuration ([a4c24a4](https://github.com/mkm29/cve-report-aggregator/commit/a4c24a4c698d623d8935a6b86680d98d86c1daf0))


### Code Refactoring

* Simplify Docker build workflow by removing unnecessary conditions and improving version handling ([6e8dc4f](https://github.com/mkm29/cve-report-aggregator/commit/6e8dc4f4785e6350529b379c1462736633a09efa))
* Simplify Docker build workflow by removing unnecessary conditions and improving version handling ([be41e7e](https://github.com/mkm29/cve-report-aggregator/commit/be41e7efb8b56cf563db262182440e8b3ec56af1))

## [0.2.0](https://github.com/mkm29/cve-report-aggregator/compare/v0.1.0...v0.2.0) (2025-10-18)


### Features

* Add branch protection and CI workflows for Git Flow ([5db7c5d](https://github.com/mkm29/cve-report-aggregator/commit/5db7c5d00712764959632d9105aaecc747977351))
* Add branch protection and CI workflows for Git Flow ([bc7ac6a](https://github.com/mkm29/cve-report-aggregator/commit/bc7ac6a67c81fcab33b7d1523d7578df33cb9583))
* Add Codecov token and slug for unit test coverage uploads ([8ed43cc](https://github.com/mkm29/cve-report-aggregator/commit/8ed43cc52a35f4c7ce987a00751ed4d1f2ec78b6))
* Add comprehensive unit tests ([29e44da](https://github.com/mkm29/cve-report-aggregator/commit/29e44dab24b1748166b14ba12836f1f4c534702b))
* add Dockerfile and update README with Docker usage instructions ([9b5208a](https://github.com/mkm29/cve-report-aggregator/commit/9b5208a54658f649f23d90bb9e0e888968be237b))
* add Dockerfile and update README with Docker usage instructions ([63a18f2](https://github.com/mkm29/cve-report-aggregator/commit/63a18f282333153a39d0528d4c16eb6d71b71ad4))
* add highest severity selection for vulnerability deduplication ([745c231](https://github.com/mkm29/cve-report-aggregator/commit/745c2313e26f18b30652095feb5cfeff29b27035))
* add highest severity selection for vulnerability deduplication ([896053c](https://github.com/mkm29/cve-report-aggregator/commit/896053ca88df1626108862a8012b438a84bb869f))
* add scanner source tracking and update CLI options for highest score selection ([276f96e](https://github.com/mkm29/cve-report-aggregator/commit/276f96eb45d2abbcd652b2ee9203aa3b29e8d4b8))
* add scanner source tracking and update CLI options for highest score selection ([8620258](https://github.com/mkm29/cve-report-aggregator/commit/862025857fd7a1601d09ff8ba6db0d0a5dc8836f))
* Add unit and integration tests for vulnerability deduplication and severity scoring ([7e2b3dc](https://github.com/mkm29/cve-report-aggregator/commit/7e2b3dcfdbdb569f9bf2088077f12c41dacf4de6))
* configured pyproject.toml to use utils module ([18ed577](https://github.com/mkm29/cve-report-aggregator/commit/18ed577617a5cb193b240ee2314ccfc2eeb4bd01))
* configured pyproject.toml to use utils module ([8041b2f](https://github.com/mkm29/cve-report-aggregator/commit/8041b2fb5604a3bbb7ec4ad5ad2deeadad2be4f9))
* implement Docker credentials management and SOPS encryption support ([93fb183](https://github.com/mkm29/cve-report-aggregator/commit/93fb1837526bb9637a70ad58843e65dad6a993e8))
* implement Docker credentials management and SOPS encryption support ([6c20a1c](https://github.com/mkm29/cve-report-aggregator/commit/6c20a1c6a5a6750bb19394af10479db83e87a4be))


### Bug Fixes

* add contributing doc ([ca44c02](https://github.com/mkm29/cve-report-aggregator/commit/ca44c026a818d610c78ba9fe36acc1c68264fa7f))
* Enhance Dockerfile credential handling with fallback for missing secrets ([e2b0858](https://github.com/mkm29/cve-report-aggregator/commit/e2b0858a9bf0323cc0d6f51ee9af57039ce48b33))
* Enhance Dockerfile credential handling with fallback for missing secrets ([4dfcc58](https://github.com/mkm29/cve-report-aggregator/commit/4dfcc588f376a76fb2d1a713d3577972829e8bbd))
* Remove commented environment section from release workflow ([3bdbef1](https://github.com/mkm29/cve-report-aggregator/commit/3bdbef14a28508129ec48ed27311bf4583dd404d))
* Remove push trigger from Docker build workflow and refine versio… ([d948616](https://github.com/mkm29/cve-report-aggregator/commit/d94861645929706f78b1fc3ac049ebfb3265be8c))
* Remove push trigger from Docker build workflow and refine versioning logic for merged PRs ([bbbd140](https://github.com/mkm29/cve-report-aggregator/commit/bbbd140f12312b1fbed1bf8877c0162cb9bc5d84))
* tighten docker build workflow ([08b2540](https://github.com/mkm29/cve-report-aggregator/commit/08b25403c77b059f833e8e6a7b146bcbcd1316bb))
* Update conditions for Docker build job execution ([e049adf](https://github.com/mkm29/cve-report-aggregator/commit/e049adf0879b44279d205229e199877e215d7bd2))
* Update Docker build context and file path for image build ([a5a9049](https://github.com/mkm29/cve-report-aggregator/commit/a5a9049ededff89b62a345fcebc03cf03ca600ce))
* Update Docker build context and file path for image build ([056c010](https://github.com/mkm29/cve-report-aggregator/commit/056c0108046b533b36ab3b26ba6df9b19e7e2c3f))
* update logo image in README and add new logo file ([1a42b79](https://github.com/mkm29/cve-report-aggregator/commit/1a42b796e5e988079340541cc58f7ace284b0c4b))
* update logo image in README and replace old logo file ([fc3f532](https://github.com/mkm29/cve-report-aggregator/commit/fc3f53266fa329d23c301bf1c250742161f3e598))


### Documentation

* Update README to include additional badges for Python version, PyPI, CI, and Docker ([8f414a6](https://github.com/mkm29/cve-report-aggregator/commit/8f414a623dbdcf36d655b0a83c2b100c7e93cb94))
* Update README to include badges ([6872952](https://github.com/mkm29/cve-report-aggregator/commit/6872952b98c0ea653ed7ac29c86e3c7023d7f9b6))


### Code Refactoring

* add type annotations for improved type safety and clarity ([8d95f87](https://github.com/mkm29/cve-report-aggregator/commit/8d95f8765a0dbdd556c9ce314363e148e92a4bec))
* add type annotations for improved type safety and clarity ([3fb6bf1](https://github.com/mkm29/cve-report-aggregator/commit/3fb6bf1ea0810fa70adc38d9058bcef73aea1953))
* Clean up test files by removing unused imports and improving docstrings ([de32773](https://github.com/mkm29/cve-report-aggregator/commit/de32773f41b8cebfc7f9ca0ab54e5dd379273506))
* modify code structure for improved readability and maintainability ([bd0a813](https://github.com/mkm29/cve-report-aggregator/commit/bd0a813e84d64e1303a2359a31e7d03f2f036607))
* Remove disk space checks and cleanup steps from Docker build workflow ([bf4aa6f](https://github.com/mkm29/cve-report-aggregator/commit/bf4aa6f3a707fb44e395b84d95102ad1ef60607e))
* Remove disk space checks and cleanup steps from Docker build workflow ([8eb4d3b](https://github.com/mkm29/cve-report-aggregator/commit/8eb4d3b422d998a9dd904b6001da9db77caedbaa))
* update CLI entry point to conditionally display logo based on version flag ([c99ad17](https://github.com/mkm29/cve-report-aggregator/commit/c99ad17bb838d95b7112f67b6bf295a8199f296c))


### Miscellaneous Chores

* merge develop branch into main ([2316963](https://github.com/mkm29/cve-report-aggregator/commit/2316963e204977416f33b0a367c336e7142aba1b))
* removed background from logo and filled in Doug ([781f3af](https://github.com/mkm29/cve-report-aggregator/commit/781f3afb889600602ab0f978a8a1544ee5b39e9f))

## [Unreleased]

### Added

- Docker credentials management with two methods: build-time secrets and environment variables
- SOPS encryption support for credentials file (`docker/config.json`)
- Docker BuildKit secret mount for secure credential injection during build
- Entrypoint script with dual authentication support (config.json or env vars)
- Security best practices documentation for credential management
- `.sops.yaml` configuration for encrypting credentials with age key
- Multi-stage Docker build with Alpine Linux base
- Non-root user (cve-aggregator, UID 1001) for container security
- Pre-installed scanning tools in Docker image: Grype, Syft, Trivy, UDS CLI
- Rich terminal output with color-coded tables and progress indicators
- Multi-scanner support (Grype and Trivy)
- SBOM auto-detection and scanning with Grype
- Automatic conversion of Grype reports to CycloneDX format for Trivy
- CVE deduplication across multiple scan reports
- Automatic null CVSS filtering (removes invalid scores)
- CVSS 3.x-based severity selection with `--mode highest-score`
- Scanner source tracking to identify which scanner provided vulnerability data
- Occurrence tracking to count CVE appearances across images
- Click-based CLI with rich-click styling
- Comprehensive test suite with pytest
- Type annotations throughout codebase
- Package installation via pip/pipx
- Docker Compose support

### Changed

- Consolidated Docker credentials documentation into main README.md
- Updated credentials file format to JSON with `username`, `password`, and `registry` fields
- Removed volume mount references from documentation (focus on credential management)
- Simplified credential methods from 4 to 2 (build-time secrets and environment variables)
- Registry is now configurable via credentials file instead of hardcoded

### Removed

- Separate `docker/README.md` file (merged into main README)
- Docker Secrets method (Docker Swarm/Compose secrets)
- Volume-mounted credentials file method
- Support for multiple credential file locations

### Security

- Credentials must be encrypted with SOPS before committing to version control
- Decrypted credential files (\*.dec) are automatically cleaned up after build
- Build-time secrets never appear in Docker image layers
- Container runs as non-root user (UID 1001)
- System pip removed from final image to reduce attack surface
- All dependencies pinned to specific versions in Dockerfile

## [0.1.0] - 2025-01-17

### Added

- Initial release of CVE Report Aggregator
- Basic Grype report aggregation and deduplication
- Command-line interface with Click
- JSON output format with metadata, summary, and vulnerabilities
- Docker support with Dockerfile and docker-compose.yml
- MIT License
- README with usage examples and installation instructions

[0.1.0]: https://github.com/mkm29/cve-report-aggregator/releases/tag/v0.1.0
[unreleased]: https://github.com/mkm29/cve-report-aggregator/compare/v0.1.0...HEAD
