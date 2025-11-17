---
name: fabric-auth
description: Authenticate with Microsoft Fabric API using Entra ID OAuth 2.0
---

# Fabric Authentication Skill

## Purpose
Acquire and manage OAuth 2.0 access tokens for Microsoft Fabric REST API calls. This skill handles both service principal (client credentials) and delegated access flows, with intelligent token caching to minimize API calls.

## When to Use
- Before making any Fabric API request
- When an API call returns 401 Unauthorized
- When cached token is expired or within 60 seconds of expiration
- When switching between authentication contexts

## Prerequisites
- **FABRIC_TENANT_ID**: Azure/Entra tenant ID (required)
- **FABRIC_CLIENT_ID**: Application (client) ID (required)
- **FABRIC_CLIENT_SECRET**: Client secret for service principal auth (required for client credentials flow)

## Implementation Steps

### 1. Check for Cached Token
- Look for cached access token in memory or temporary file
- Verify token expiration time (must have >60 seconds remaining)
- If valid token exists, return it immediately
- If token is expired or missing, proceed to step 2

### 2. Read Credentials from Environment
```bash
TENANT_ID=$(printenv FABRIC_TENANT_ID)
CLIENT_ID=$(printenv FABRIC_CLIENT_ID)
CLIENT_SECRET=$(printenv FABRIC_CLIENT_SECRET)
```

- If any credential is missing, display setup instructions (see Error Handling section)
- Validate credential formats:
  - TENANT_ID: GUID format (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
  - CLIENT_ID: GUID format
  - CLIENT_SECRET: Non-empty string

### 3. Acquire Token via Client Credentials Flow
Make POST request to Microsoft Entra ID token endpoint:

**Endpoint:**
```
POST https://login.microsoftonline.com/{tenantId}/oauth2/v2.0/token
Content-Type: application/x-www-form-urlencoded
```

**Request Body:**
```
grant_type=client_credentials
&client_id={clientId}
&client_secret={clientSecret}
&scope=https://api.fabric.microsoft.com/.default
```

**Using curl:**
```bash
curl -X POST "https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=${CLIENT_ID}" \
  -d "client_secret=${CLIENT_SECRET}" \
  -d "scope=https://api.fabric.microsoft.com/.default"
```

**Expected Response (200 OK):**
```json
{
  "token_type": "Bearer",
  "expires_in": 3599,
  "ext_expires_in": 3599,
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 4. Cache Token with Expiration
- Extract `access_token` from response
- Calculate expiration timestamp: current_time + (expires_in - 60 seconds buffer)
- Store token and expiration in memory or temporary file:
  ```json
  {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "expires_at": 1699999999,
    "token_type": "Bearer"
  }
  ```
- Token cache location suggestion: `/tmp/fabric_token_cache.json` (Linux/Mac) or `%TEMP%\fabric_token_cache.json` (Windows)

### 5. Return Access Token
- Return the `access_token` string for use in Authorization header
- Token should be used as: `Authorization: Bearer {access_token}`

## Input Parameters
None (reads from environment variables)

## Output
- **Success**: Access token string (JWT format)
- **Failure**: Error message with actionable instructions

## Error Handling

### Missing Credentials
**Error Message:**
```
❌ Fabric API credentials not configured

Please set the following environment variables:
  export FABRIC_TENANT_ID="your-tenant-id"
  export FABRIC_CLIENT_ID="your-client-id"
  export FABRIC_CLIENT_SECRET="your-client-secret"

To find these values:
1. Azure Portal → Azure Active Directory → App registrations
2. Select your application (or create new one)
3. Overview page shows Tenant ID and Client ID
4. Certificates & secrets → Create new client secret

Run `/fabric:configure` for interactive setup.
```

### Invalid Credentials (400/401)
**Error Message:**
```
❌ Authentication failed: Invalid credentials

Error details: {error_description from API}

Possible causes:
- Client ID or Client Secret is incorrect
- Service principal doesn't exist or is disabled
- Tenant ID is incorrect

Please verify your credentials and try again.
Run `/fabric:configure` to update credentials.
```

### Service Principal Not Enabled (403)
**Error Message:**
```
❌ Service principal not enabled for Fabric API

To enable:
1. Go to Fabric Admin Portal → Tenant settings
2. Find "Service principals can use Fabric APIs"
3. Enable and add your service principal
4. Wait 15 minutes for changes to propagate

Alternatively, use delegated auth flow (not yet implemented).
```

### Network Errors
- Implement exponential backoff: 1s, 2s, 4s, 8s
- Maximum 3 retry attempts
- If all retries fail, display:
```
❌ Network error connecting to Microsoft Entra ID

Please check:
- Internet connectivity
- Firewall/proxy settings
- Service status: https://status.azure.com

Error: {error_message}
```

### Token Endpoint Rate Limiting (429)
- Respect `Retry-After` header from response
- Wait specified seconds before retry
- Display message to user:
```
⏳ Authentication rate limited. Waiting {retry_after} seconds...
```

## Security Best Practices
1. **Never log tokens**: Do not print access tokens to console or logs
2. **Secure storage**: Use appropriate file permissions for token cache (0600 on Unix)
3. **Token rotation**: Implement token refresh before expiration
4. **Credential protection**: Never commit credentials to git repositories
5. **Environment isolation**: Use separate service principals for dev/test/prod

## Performance Optimization
- **Token caching**: Reduces token acquisition from ~500ms to <1ms
- **Expiration buffer**: 60-second buffer prevents race conditions
- **Lazy loading**: Only acquire token when needed
- **Reuse across commands**: Cache persists across multiple command invocations

## Example Usage

### First API Call (Token Acquisition)
```bash
# User runs a Fabric command
/fabric:list-workspaces

# Skill is invoked automatically
# → Checks cache: empty
# → Reads environment variables
# → Acquires token from Entra ID (~500ms)
# → Caches token
# → Returns token to command
# Command proceeds with API call
```

### Subsequent API Calls (Token Reuse)
```bash
# User runs another Fabric command
/fabric:get-workspace abc123

# Skill is invoked automatically
# → Checks cache: valid token found (<1ms)
# → Returns cached token
# Command proceeds with API call
```

### Token Expiration Scenario
```bash
# 59 minutes after initial token acquisition
/fabric:create-lakehouse my-workspace my-lakehouse

# Skill is invoked automatically
# → Checks cache: token expires in 30 seconds
# → Acquires new token from Entra ID
# → Updates cache
# → Returns new token
# Command proceeds with API call
```

## Testing Checklist
- [ ] Valid credentials → Token acquired successfully
- [ ] Missing TENANT_ID → Clear error message with setup instructions
- [ ] Missing CLIENT_ID → Clear error message
- [ ] Missing CLIENT_SECRET → Clear error message
- [ ] Invalid credentials → 401 error with helpful message
- [ ] Network failure → Retry logic works, clear error after 3 attempts
- [ ] Token caching → Second call uses cached token (<1ms)
- [ ] Token expiration → New token acquired automatically
- [ ] Rate limiting → Respects Retry-After header

## Related Commands
- `/fabric:configure` - Interactive credential setup
- `/fabric:test-connection` - Verify authentication works

## API Documentation
- **Entra ID Token Endpoint**: https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-client-creds-grant-flow
- **Fabric API Authentication**: https://learn.microsoft.com/en-us/rest/api/fabric/articles/get-started/fabric-api-quickstart
