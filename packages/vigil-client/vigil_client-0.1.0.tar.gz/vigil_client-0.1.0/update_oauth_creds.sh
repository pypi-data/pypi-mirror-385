#!/bin/bash
# Script to update .env with OAuth credentials

echo "🔐 Clerk OAuth Setup for Vigil Client"
echo "======================================"
echo ""
echo "You need to create an OAuth application in Clerk Dashboard."
echo "Go to: https://dashboard.clerk.dev"
echo "Then: Applications → top-kid-83 → OAuth Applications → Add OAuth Application"
echo ""
echo "Configuration:"
echo "- Name: vigil-client"
echo "- Type: Public"
echo "- Redirect URI: http://localhost:8080/callback"
echo "- Scopes: openid, email, profile"
echo ""
echo "After creating the OAuth app, you'll get:"
echo "- Client ID: oauth_xxxxxxxxxxxxxxxxxxxxxxxx"
echo "- Client Secret: oauth_xxxxxxxxxxxxxxxxxxxxxxxx"
echo ""

read -p "Enter OAuth Client ID (starts with oauth_): " OAUTH_CLIENT_ID
read -p "Enter OAuth Client Secret (starts with oauth_): " OAUTH_CLIENT_SECRET

if [[ $OAUTH_CLIENT_ID == oauth_* ]] && [[ $OAUTH_CLIENT_SECRET == oauth_* ]]; then
    # Backup existing .env
    cp .env .env.backup

    # Update .env with OAuth credentials
    cat > .env << EOF
# Clerk OAuth Application Configuration
CLERK_CLIENT_ID=$OAUTH_CLIENT_ID
CLERK_CLIENT_SECRET=$OAUTH_CLIENT_SECRET
CLERK_DOMAIN=https://top-kid-83.clerk.accounts.dev

# Vigil Platform Configuration
VIGIL_API_URL=http://localhost:3002

# Optional: Custom redirect URI (defaults to http://localhost:8080/callback)
# CLERK_REDIRECT_URI=http://localhost:8080/callback
EOF

    echo ""
    echo "✅ Updated .env with OAuth credentials"
    echo "✅ Backup saved as .env.backup"
    echo ""
    echo "Test authentication:"
    echo "source venv/bin/activate && source .env && python3 -m vigil_client.cli login login"
else
    echo "❌ Invalid credentials. Client ID and Secret must start with 'oauth_'"
    echo "Make sure you're using OAuth application credentials, not publishable keys."
fi
