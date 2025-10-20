#!/bin/bash

set -euo pipefail

# function to handle termination signals
_term() {
	echo "Termination signal received. Shutting down gracefully..."
	# Add any cleanup commands here
	exit 0
}
# trap termination signals
trap _term SIGTERM SIGINT

check_docker_config() {
	# Check if Docker config.json exists with auth
	if [[ -f "$DOCKER_CONFIG/config.json" ]]; then
		echo "Found Docker authentication in $DOCKER_CONFIG/config.json"
		return 0
	fi
	return 1
}

# No password file reading - only environment variables supported for runtime auth

# Function to check for required environment variables
check_env_vars() {
	local required_vars=("REGISTRY_URL" "UDS_USERNAME" "UDS_PASSWORD")
	for var in "${required_vars[@]}"; do
		if [[ -z "${!var:-}" ]]; then
			echo "Error: Environment variable '$var' is not set."
			echo "Please provide it via -e $var=<value>"
			exit 1
		fi
	done
}

# Function to login to registry
login_to_registry() {
	echo "Logging in to registry: $REGISTRY_URL..."
	if ! echo "$PASSWORD" | uds zarf tools registry login "$REGISTRY_URL" --username "$UDS_USERNAME" --password-stdin; then
		echo "Error: Failed to login to registry."
		exit 1
	fi
	echo "Successfully logged in to registry."
}

# Main script execution

# Check if Docker config.json already has authentication (baked-in during build)
if check_docker_config; then
	echo "Using build-time Docker authentication from config.json"
	echo "Skipping registry login..."
else
	echo "No Docker config found, performing runtime registry login with environment variables..."
	check_env_vars
	# Export PASSWORD for login function
	export PASSWORD="${UDS_PASSWORD}"
	login_to_registry
fi

# Execute the cve-report-aggregator with provided arguments
exec cve-report-aggregator "$@"
