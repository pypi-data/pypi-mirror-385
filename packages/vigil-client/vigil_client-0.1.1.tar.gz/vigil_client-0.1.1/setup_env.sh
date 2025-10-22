#!/bin/bash
# Setup script for vigil-client environment variables

echo "🔐 Setting up vigil-client environment variables..."

# Create .env file with your actual Clerk credentials
cat > .env << 'EOF'
# Clerk Authentication Configuration
CLERK_CLIENT_ID=pk_test_dG9wLWtpZC04My5jbGVyay5hY2NvdW50cy5kZXYk
CLERK_CLIENT_SECRET=sk_test_6Dn200cjIj69XWUsr8tbhmgW0I8p5NaUEpQywhIko5
CLERK_DOMAIN=https://top-kid-83.clerk.accounts.dev

# Vigil Platform Configuration
VIGIL_API_URL=http://localhost:3002

# Optional: Custom redirect URI (defaults to http://localhost:8080/callback)
# CLERK_REDIRECT_URI=http://localhost:8080/callback
EOF

echo "✅ Created .env file with your Clerk credentials"

# Export variables for current session
export CLERK_CLIENT_ID="pk_test_dG9wLWtpZC04My5jbGVyay5hY2NvdW50cy5kZXYk"
export CLERK_CLIENT_SECRET="sk_test_6Dn200cjIj69XWUsr8tbhmgW0I8p5NaUEpQywhIko5"
export CLERK_DOMAIN="https://top-kid-83.clerk.accounts.dev"
export VIGIL_API_URL="http://localhost:3002"

echo "✅ Environment variables exported for current session"
echo ""
echo "Next steps:"
echo "1. Make sure your apps/api is running on http://localhost:3002"
echo "2. Test authentication: vigil login"
echo "3. Check status: vigil whoami"
