---
name: fabric-auth
description: Authenticate with Microsoft Fabric API using Entra ID OAuth 2.0 (service principal or delegated user auth)
---

# Fabric Authentication Skill

## Purpose
Acquire and manage OAuth 2.0 access tokens for Microsoft Fabric REST API calls. This skill supports two authentication methods:
1. **Service Principal** (client credentials flow) - for automation and admin tasks
2. **Delegated User** (authorization code flow) - for personal use, no admin required

The skill automatically detects the authentication type and handles token caching, refresh, and expiration.

## When to Use
- Before making any Fabric API request
- When an API call returns 401 Unauthorized
- When cached token is expired or within 60 seconds of expiration
- When switching between authentication contexts

## Prerequisites

### For Service Principal Authentication
- **FABRIC_TENANT_ID**: Azure/Entra tenant ID
- **FABRIC_CLIENT_ID**: Application (client) ID
- **FABRIC_CLIENT_SECRET**: Client secret
- **FABRIC_AUTH_TYPE**: Set to `service_principal` (or leave unset for default)

### For Delegated User Authentication
- **FABRIC_AUTH_TYPE**: Set to `delegated`
- **FABRIC_CLIENT_ID**: Optional - uses default public client if not provided
- **Token cache**: `~/.fabric/token_cache.json` (created automatically)

## Implementation Steps

### 1. Determine Authentication Type
```bash
AUTH_TYPE="${FABRIC_AUTH_TYPE:-service_principal}"

if [ "$AUTH_TYPE" = "delegated" ]; then
  echo "Using delegated user authentication"
  # Check for token cache at ~/.fabric/token_cache.json
else
  echo "Using service principal authentication"
  # Use client credentials flow
fi
```

### 2. Check for Cached Token

**Token Cache Locations:**
- **Service Principal**: `/tmp/fabric_token_cache_sp.json` or `%TEMP%\fabric_token_cache_sp.json`
- **Delegated**: `~/.fabric/token_cache.json`

**Validation:**
- Look for cached access token in appropriate location
- Verify token expiration time (must have >60 seconds remaining)
- For delegated auth: Check if refresh token exists
- If valid token exists, return it immediately
- If token is expired or missing, proceed to step 3

### 3. Branch Based on Authentication Type

#### Path A: Service Principal (Client Credentials Flow)

**3A.1 Read Credentials from Environment**
```bash
TENANT_ID=$(printenv FABRIC_TENANT_ID)
CLIENT_ID=$(printenv FABRIC_CLIENT_ID)
CLIENT_SECRET=$(printenv FABRIC_CLIENT_SECRET)
```

- If any credential is missing, display setup instructions
- Validate credential formats:
  - TENANT_ID: GUID format
  - CLIENT_ID: GUID format
  - CLIENT_SECRET: Non-empty string

**3A.2 Acquire Token via Client Credentials Flow**
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

#### Path B: Delegated User (Authorization Code Flow with Token Refresh)

**3B.1 Check Token Cache**
```bash
TOKEN_CACHE="$HOME/.fabric/token_cache.json"

if [ -f "$TOKEN_CACHE" ]; then
  ACCESS_TOKEN=$(jq -r '.access_token' "$TOKEN_CACHE")
  REFRESH_TOKEN=$(jq -r '.refresh_token' "$TOKEN_CACHE")
  EXPIRES_AT=$(jq -r '.expires_at' "$TOKEN_CACHE")
  CURRENT_TIME=$(date +%s)

  # If access token is still valid (>60s remaining)
  if [ $EXPIRES_AT -gt $((CURRENT_TIME + 60)) ]; then
    echo "$ACCESS_TOKEN"
    exit 0
  fi

  # Access token expired, try refresh token
  if [ -n "$REFRESH_TOKEN" ] && [ "$REFRESH_TOKEN" != "null" ]; then
    # Proceed to step 3B.3 (refresh token flow)
  fi
fi
```

**3B.2 No Valid Token Found**
If no valid cached token exists, user must authenticate:
```
❌ Authentication required

Please run: /fabric:login

This will open a browser window to sign in with your Microsoft account.
```

**3B.3 Refresh Access Token Using Refresh Token**

**Default Public Client ID** (Hybrid approach):
```bash
# Use custom client ID if provided, otherwise use default
DEFAULT_CLIENT_ID="04b07795-8ddb-461a-bbee-02f9e1bf7b46"  # Microsoft Azure CLI public client
CLIENT_ID="${FABRIC_CLIENT_ID:-$DEFAULT_CLIENT_ID}"
```

**Token Refresh Request:**
```bash
curl -X POST "https://login.microsoftonline.com/organizations/oauth2/v2.0/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token" \
  -d "client_id=${CLIENT_ID}" \
  -d "refresh_token=${REFRESH_TOKEN}" \
  -d "scope=https://api.fabric.microsoft.com/Item.ReadWrite.All offline_access"
```

**Expected Response:**
```json
{
  "token_type": "Bearer",
  "expires_in": 3599,
  "access_token": "eyJ0eXAiOiJKV1Qi...",
  "refresh_token": "0.AXoA...",
  "scope": "https://api.fabric.microsoft.com/Item.ReadWrite.All"
}
```

**3B.4 Handle Refresh Token Expiration**
If refresh token is expired or invalid (400/401 error):
```
❌ Authentication expired

Your login session has expired. Please sign in again:
  /fabric:login
```

### 4. Cache Token with Expiration

**For Service Principal:**
- Extract `access_token` from response
- Calculate expiration timestamp: current_time + (expires_in - 60 seconds buffer)
- Store in `/tmp/fabric_token_cache_sp.json`:
  ```json
  {
    "auth_type": "service_principal",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "expires_at": 1699999999,
    "token_type": "Bearer"
  }
  ```

**For Delegated User:**
- Extract both `access_token` and `refresh_token` from response
- Calculate expiration timestamp: current_time + (expires_in - 60 seconds buffer)
- Store in `~/.fabric/token_cache.json`:
  ```json
  {
    "auth_type": "delegated",
    "access_token": "eyJ0eXAiOiJKV1Qi...",
    "refresh_token": "0.AXoA...",
    "expires_at": 1699999999,
    "token_type": "Bearer",
    "scope": "https://api.fabric.microsoft.com/Item.ReadWrite.All"
  }
  ```
- Create `~/.fabric` directory if it doesn't exist
- Set file permissions to 0600 (owner read/write only) for security

### 5. Return Access Token
- Return the `access_token` string for use in Authorization header
- Token should be used as: `Authorization: Bearer {access_token}`

## Input Parameters
None (reads from environment variables)

## Output
- **Success**: Access token string (JWT format)
- **Failure**: Error message with actionable instructions

## Error Handling

### Missing Credentials (Service Principal)
**Error Message:**
```
❌ Service Principal credentials not configured

Please set the following environment variables:
  export FABRIC_TENANT_ID="your-tenant-id"
  export FABRIC_CLIENT_ID="your-client-id"
  export FABRIC_CLIENT_SECRET="your-client-secret"
  export FABRIC_AUTH_TYPE="service_principal"

Options:
1. Run `/fabric:configure` for interactive setup
2. Or switch to user authentication: `/fabric:login`
   (no admin access required)
```

### Missing Authentication (Delegated)
**Error Message:**
```
❌ Not authenticated

Please sign in with your Microsoft account:
  /fabric:login

This will open a browser window for authentication.
No Azure admin access required.

Alternatively, use service principal: /fabric:configure
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
