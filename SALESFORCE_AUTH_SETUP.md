# Salesforce OAuth Authentication Setup

This guide explains how to configure Onyx to use Salesforce OAuth for user authentication.

## Prerequisites

- Access to Salesforce with permissions to create Connected Apps
- Onyx deployment (self-hosted or cloud)

## Step 1: Create a Salesforce Connected App

1. **Log in to Salesforce**
   - Go to https://login.salesforce.com (or https://test.salesforce.com for sandbox)
   - Log in with administrator credentials

2. **Navigate to App Manager**
   - Click the gear icon (Setup) in the top right
   - In Quick Find, search for "App Manager"
   - Click "App Manager"

3. **Create New Connected App**
   - Click "New Connected App" button
   - Fill in basic information:
     - **Connected App Name**: `Onyx Authentication`
     - **API Name**: `Onyx_Authentication`
     - **Contact Email**: Your email address

4. **Enable OAuth Settings**
   - Check "Enable OAuth Settings"
   - **Callback URL**: `https://your-onyx-domain.com/auth/salesforce/callback`
     - For local development: `http://localhost:3000/auth/salesforce/callback`
   - **Selected OAuth Scopes**: Add these scopes:
     - `Access the identity URL service (id, profile, email, address, phone)`
     - `Manage user data via APIs (api)`
     - `Perform requests at any time (refresh_token, offline_access)`
   - **Require Secret for Web Server Flow**: Check this box
   - **Require Secret for Refresh Token Flow**: Check this box

5. **Save and Continue**
   - Click "Save"
   - Click "Continue" on the confirmation page

6. **Retrieve OAuth Credentials**
   - After saving, you'll see the Connected App details
   - Click "Manage Consumer Details" to view:
     - **Consumer Key** (this is your Client ID)
     - **Consumer Secret** (this is your Client Secret)
   - Save these credentials securely

## Step 2: Configure Onyx

### Environment Variables

Add the following to your `.env` file or environment configuration:

```bash
# Set authentication type to Salesforce OAuth
AUTH_TYPE=salesforce_oauth

# Salesforce OAuth credentials from your Connected App
SALESFORCE_OAUTH_CLIENT_ID=your_consumer_key_here
SALESFORCE_OAUTH_CLIENT_SECRET=your_consumer_secret_here

# Salesforce instance URL
# For production: https://login.salesforce.com
# For sandbox: https://test.salesforce.com
SALESFORCE_INSTANCE_URL=https://login.salesforce.com

# Set your Onyx web domain (required for OAuth redirect)
WEB_DOMAIN=https://your-onyx-domain.com
```

### Docker Compose

If using Docker Compose, update your `docker-compose.yml` or environment file:

```yaml
services:
  api_server:
    environment:
      - AUTH_TYPE=salesforce_oauth
      - SALESFORCE_OAUTH_CLIENT_ID=${SALESFORCE_OAUTH_CLIENT_ID}
      - SALESFORCE_OAUTH_CLIENT_SECRET=${SALESFORCE_OAUTH_CLIENT_SECRET}
      - SALESFORCE_INSTANCE_URL=${SALESFORCE_INSTANCE_URL:-https://login.salesforce.com}
      - WEB_DOMAIN=${WEB_DOMAIN}

  web_server:
    environment:
      - WEB_DOMAIN=${WEB_DOMAIN}
```

## Step 3: Restart Services

Restart your Onyx services to apply the new configuration:

```bash
# Docker Compose
docker-compose down
docker-compose up -d

# Kubernetes
kubectl rollout restart deployment/onyx-api-server
kubectl rollout restart deployment/onyx-web-server
```

## Step 4: Test Authentication

1. Navigate to your Onyx login page: `https://your-onyx-domain.com/auth/login`
2. You should see a "Continue with Salesforce" button
3. Click the button to initiate the OAuth flow
4. You'll be redirected to Salesforce to authorize the application
5. After authorization, you'll be redirected back to Onyx and logged in

## Troubleshooting

### Error: "redirect_uri_mismatch"

**Problem**: The callback URL doesn't match what's configured in Salesforce.

**Solution**:
- Verify the callback URL in your Salesforce Connected App matches exactly: `https://your-onyx-domain.com/auth/salesforce/callback`
- Check that `WEB_DOMAIN` environment variable is set correctly

### Error: "invalid_client_id" or "invalid_client_secret"

**Problem**: OAuth credentials are incorrect.

**Solution**:
- Double-check the Consumer Key and Consumer Secret from Salesforce
- Ensure there are no extra spaces or newlines when copying credentials
- Verify the credentials are set correctly in your environment variables

### Error: "user_not_found" or User Cannot Login

**Problem**: User email from Salesforce doesn't match existing Onyx user.

**Solution**:
- Onyx associates users by email address
- Ensure the email in Salesforce matches the email in Onyx
- Check if email domain restrictions are configured (`VALID_EMAIL_DOMAINS`)

### Salesforce Sandbox Issues

**Problem**: Can't authenticate with sandbox environment.

**Solution**:
- Use the sandbox URL: `SALESFORCE_INSTANCE_URL=https://test.salesforce.com`
- Ensure your Connected App is created in the sandbox environment
- Sandbox credentials are separate from production

## Security Best Practices

1. **Keep Credentials Secret**: Never commit OAuth credentials to version control
2. **Use Environment Variables**: Store credentials in environment variables or secret management systems
3. **Restrict Scopes**: Only request the minimum OAuth scopes needed
4. **Enable IP Restrictions**: Configure IP restrictions in Salesforce Connected App settings if needed
5. **Monitor Access**: Review OAuth tokens and access logs regularly in Salesforce

## OAuth Flow Details

The Salesforce OAuth flow in Onyx works as follows:

1. User clicks "Continue with Salesforce"
2. Frontend requests authorization URL from backend (`/auth/salesforce/authorize`)
3. Backend generates OAuth state token and returns Salesforce authorization URL
4. User is redirected to Salesforce login/authorization page
5. User approves the application
6. Salesforce redirects to callback URL with authorization code
7. Backend exchanges code for access token and refresh token
8. Backend retrieves user profile from Salesforce
9. User is created/updated in Onyx database
10. Session cookie is set and user is logged in

## Additional Configuration

### Email Domain Restrictions

To restrict authentication to specific email domains:

```bash
VALID_EMAIL_DOMAINS=yourcompany.com,partner.com
```

### Session Configuration

Configure session timeout:

```bash
SESSION_EXPIRE_TIME_SECONDS=604800  # 7 days (default)
```

### Multi-Organization Support

If you have multiple Salesforce orgs, you can configure multiple Connected Apps and use different instance URLs. However, Onyx only supports one Salesforce instance at a time per deployment.

## Support

For issues or questions:
- GitHub Issues: https://github.com/onyx-dot-app/onyx/issues
- Slack Community: https://join.slack.com/t/onyx-dot-app/shared_invite/...
