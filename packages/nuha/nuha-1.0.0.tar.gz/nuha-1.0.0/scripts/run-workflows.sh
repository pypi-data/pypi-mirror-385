#!/bin/bash

# Script to test CI workflow locally with act
# This script sets up the necessary environment variables for local testing

set -e

echo "🚀 Testing CI workflow locally with act..."
echo ""

# Check if act is installed
if ! command -v act &> /dev/null; then
    echo "❌ 'act' is not installed. Please install it first:"
    echo "   curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash"
    exit 1
fi

# Set mock environment variables for local testing
export ACTIONS_RUNTIME_TOKEN="mock_token_for_local_testing"
export ACTIONS_CACHE_URL="mock_cache_url_for_local_testing"
export GITHUB_REPOSITORY="u3n-ai/nuha"
export GITHUB_SHA="local-testing-sha"
export GITHUB_REF="refs/heads/main"
export GITHUB_RUN_ID="local-run-123"
export GITHUB_RUN_NUMBER="1"

echo "🔧 Environment variables set for local testing:"
echo "   ACTIONS_RUNTIME_TOKEN=${ACTIONS_RUNTIME_TOKEN}"
echo "   ACTIONS_CACHE_URL=${ACTIONS_CACHE_URL}"
echo "   GITHUB_REPOSITORY=${GITHUB_REPOSITORY}"
echo ""

# Run act with the CI workflow
echo "🏃 Running CI workflow..."
echo "   Command: act -W .github/workflows/ci.yml --container-architecture linux/amd64"
echo ""

act -W .github/workflows/ci.yml --container-architecture linux/amd64

echo ""
echo "✅ CI workflow test completed!"
echo ""
echo "📝 Notes:"
echo "   - Artifacts will be uploaded to mock storage (for testing only)"
echo "   - Build artifacts will be available in dist/ directory"
echo "   - Test results will be available in htmlcov/, coverage.xml, etc."
echo "   - Some GitHub-specific features may behave differently locally"
