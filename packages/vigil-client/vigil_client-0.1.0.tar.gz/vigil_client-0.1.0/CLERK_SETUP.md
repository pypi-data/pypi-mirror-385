# Clerk Authentication Setup for Vigil Client

This guide will help you set up Clerk authentication for the vigil-client package.

## 1. Create a Clerk Application

1. Go to [Clerk Dashboard](https://dashboard.clerk.dev)
2. Sign up or log in to your account
3. Click "Create Application"
4. Choose a name for your application (e.g., "Vigil Platform")
5. Select your preferred sign-in methods (Email, Google, GitHub, etc.)

## 2. Configure OAuth Settings

1. In your Clerk dashboard, go to **Configure > OAuth**
2. Add the following redirect URI:
   ```
   http://localhost:8080/callback
   ```
3. Save the configuration

## 3. Get Your Credentials

1. Go to **Configure > API Keys**
2. Copy the following values:
   - **Publishable Key** (this is your `CLERK_CLIENT_ID`)
   - **Secret Key** (this is your `CLERK_CLIENT_SECRET`)
3. Note your Clerk domain (e.g., `https://your-app.clerk.accounts.dev`)

## 4. Set Environment Variables

Create a `.env` file in your project root or set these environment variables:

```bash
# Copy from env.example
cp env.example .env

# Edit .env with your actual values
export CLERK_CLIENT_ID="pk_test_dG9wLWtpZC04My5jbGVyay5hY2NvdW50cy5kZXYk"
export CLERK_CLIENT_SECRET="sk_test_6Dn200cjIj69XWUsr8tbhmgW0I8p5NaUEpQywhIko5"
export CLERK_DOMAIN="https://top-kid-83.clerk.accounts.dev"
export VIGIL_API_URL="http://localhost:3002"
```

## 5. Install Dependencies

```bash
cd packages/vigil-client
pip install -e .
```

## 6. Test Authentication

```bash
# Test interactive login
vigil login

# Test token-based login (if you have a JWT)
vigil login --token "your_jwt_token_here"

# Check authentication status
vigil whoami

# Logout
vigil logout
```

## 7. Troubleshooting

### Common Issues

1. **"CLERK_CLIENT_ID environment variable not set"**
   - Make sure you've set the environment variables correctly
   - Check that your `.env` file is in the right location

2. **"Authentication timed out"**
   - Make sure port 8080 is available
   - Check your firewall settings
   - Try a different port by setting `CLERK_REDIRECT_URI`

3. **"Invalid redirect URI"**
   - Ensure the redirect URI in Clerk matches exactly: `http://localhost:8080/callback`
   - Check for typos in your Clerk configuration

4. **"Token verification failed"**
   - This is normal in development mode
   - The system will fall back to unverified token decoding
   - In production, ensure your Clerk domain is correct

### Development vs Production

- **Development**: JWT signature verification is optional (falls back to unverified decoding)
- **Production**: Full JWT signature verification with Clerk's public keys
- **Token Storage**: Uses system keyring for secure storage (fallback to config file)

## 8. Security Considerations

1. **Never commit your `.env` file** - it contains sensitive credentials
2. **Use different Clerk applications** for development and production
3. **Rotate your secret keys** regularly
4. **Monitor authentication logs** in your Clerk dashboard

## 9. Integration with Your Platform

Once authentication is working, you can integrate with your platform API:

```python
from vigil_client import VigilClient

# The client will automatically use the stored authentication
client = VigilClient()

# Make authenticated requests
artifacts = client.artifacts.list()
```

## 10. Next Steps

- Set up your platform API to validate Clerk JWTs
- Implement user management and organization features
- Add role-based access control (RBAC)
- Set up webhook endpoints for user events
