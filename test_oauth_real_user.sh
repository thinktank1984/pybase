#!/bin/bash
# OAuth Testing Script for Real User
# Tests OAuth functionality with real user credentials: ed.s.sharood@gmail.com

set -e

echo "========================================="
echo "OAuth Real User Testing"
echo "User: Ed (ed.s.sharood@gmail.com)"
echo "========================================="
echo ""

# Check if running in Docker or locally
if [ -f /.dockerenv ]; then
    CONTEXT="docker"
    echo "Running in Docker container"
else
    CONTEXT="local"
    echo "Running locally"
fi

# Detect Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found"
    exit 1
fi

# Check if OAuth encryption key is set
if [ -z "$OAUTH_TOKEN_ENCRYPTION_KEY" ]; then
    echo "⚠️  OAUTH_TOKEN_ENCRYPTION_KEY not set"
    echo "   Generating temporary key for testing..."
    export OAUTH_TOKEN_ENCRYPTION_KEY=$($PYTHON_CMD -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')
    echo "   ✅ Temporary encryption key generated"
else
    echo "✅ OAuth encryption key is set"
fi

# Check OAuth provider configuration
echo ""
echo "Checking OAuth provider configuration:"
if [ -n "$GOOGLE_CLIENT_ID" ]; then
    echo "  ✅ Google OAuth configured"
    GOOGLE_CONFIGURED=true
else
    echo "  ⚠️  Google OAuth not configured (optional for database tests)"
    GOOGLE_CONFIGURED=false
fi

if [ -n "$GITHUB_CLIENT_ID" ]; then
    echo "  ✅ GitHub OAuth configured"
else
    echo "  ⚠️  GitHub OAuth not configured (optional)"
fi

if [ -n "$MICROSOFT_CLIENT_ID" ]; then
    echo "  ✅ Microsoft OAuth configured"
else
    echo "  ⚠️  Microsoft OAuth not configured (optional)"
fi

if [ -n "$FACEBOOK_APP_ID" ]; then
    echo "  ✅ Facebook OAuth configured"
else
    echo "  ⚠️  Facebook OAuth not configured (optional)"
fi

echo ""
echo "========================================="
echo "Running OAuth Integration Tests"
echo "========================================="
echo ""

# Run the tests
if [ "$CONTEXT" = "docker" ]; then
    pytest /app/integration_tests/test_oauth_real_user.py -v --tb=short "$@"
else
    cd "$(dirname "$0")"
    uv run pytest integration_tests/test_oauth_real_user.py -v --tb=short "$@"
fi

TEST_EXIT_CODE=$?

echo ""
echo "========================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All OAuth tests passed!"
else
    echo "❌ Some OAuth tests failed"
fi
echo "========================================="
echo ""

if [ "$GOOGLE_CONFIGURED" = false ]; then
    echo "💡 To test full OAuth flows:"
    echo "   1. Set up OAuth provider credentials (see runtime/documentation/OAUTH_SETUP.md)"
    echo "   2. Set environment variables:"
    echo "      export GOOGLE_CLIENT_ID=your-client-id"
    echo "      export GOOGLE_CLIENT_SECRET=your-client-secret"
    echo "   3. Start the application:"
    echo "      docker compose -f docker/docker-compose.yaml up runtime"
    echo "   4. Test manually at: http://localhost:8081/auth/login"
    echo "   5. Log in with: ed.s.sharood@gmail.com"
    echo ""
fi

echo "📚 Documentation:"
echo "   - OAuth Setup: runtime/documentation/OAUTH_SETUP.md"
echo "   - Testing Guide: documentation/OAUTH_TESTING_GUIDE.md"
echo "   - Test Config: integration_tests/oauth_test_config.yaml"
echo ""

exit $TEST_EXIT_CODE

