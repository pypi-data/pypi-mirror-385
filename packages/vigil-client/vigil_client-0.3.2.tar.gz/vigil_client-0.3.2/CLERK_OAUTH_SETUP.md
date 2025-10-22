# Clerk OAuth Setup for Vigil Client

## The Problem
You're getting `"invalid_client"` error because you're using Clerk's **publishable key** (`pk_test_...`) as an OAuth client ID. Clerk OAuth requires a separate OAuth application.

## The Solution

### 1. Create OAuth Application in Clerk

1. Go to [Clerk Dashboard](https://dashboard.clerk.dev)
2. Select your application: `top-kid-83`
3. Navigate to **Applications** → **[Your App]** → **OAuth Applications**
4. Click **"Add OAuth Application"**

### 2. Configure OAuth Application

**Application Name:** `vigil-client`
**Application Type:** `Public` (for CLI apps)

**Redirect URIs:**
```
http://localhost:8080/callback
```

**Scopes:**
- `openid`
- `email`
- `profile`

### 3. Get OAuth Credentials

After creating the OAuth application, you'll get:
- **Client ID:** `oauth_...` (not `pk_test_...`)
- **Client Secret:** `oauth_...` (not `sk_test_...`)

### 4. Update Environment Variables

Update your `.env` file:

```bash
# Clerk OAuth Application Configuration
CLERK_CLIENT_ID=oauth_xxxxxxxxxxxxxxxxxxxxxxxx
CLERK_CLIENT_SECRET=oauth_xxxxxxxxxxxxxxxxxxxxxxxx
CLERK_DOMAIN=https://top-kid-83.clerk.accounts.dev

# Vigil Platform Configuration
VIGIL_API_URL=http://localhost:3002
```

### 5. Test Authentication

```bash
source venv/bin/activate
source .env
python3 -m vigil_client.cli login login
```

## Alternative: Use Existing OAuth App

If you already have an OAuth application configured for your web app (`cofactor-app`), you can reuse it by:

1. Adding `http://localhost:8080/callback` to its redirect URIs
2. Using its OAuth client ID and secret

## Troubleshooting

**Still getting `invalid_client`?**
- Double-check the client ID starts with `oauth_`
- Ensure redirect URI `http://localhost:8080/callback` is configured
- Verify the OAuth application is active

**Browser doesn't open?**
- Copy the printed URL and open it manually
- Make sure port 8080 is available

**Token exchange fails?**
- Check that client secret is correct
- Verify the OAuth application has the right scopes
