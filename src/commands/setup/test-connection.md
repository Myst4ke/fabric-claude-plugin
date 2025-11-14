---
description: Test Microsoft Fabric API connectivity and authentication
argument-hint: [--verbose]
---

# /fabric:test-connection

## Purpose
Verify that Microsoft Fabric API credentials are configured correctly and that the plugin can successfully authenticate and communicate with the Fabric API. This command performs a complete authentication flow and makes a test API call to validate the setup.

## Arguments
- `--verbose`: Optional. Display detailed diagnostic information including token details (partially masked) and response headers

## Prerequisites
- Environment variables must be set:
  - FABRIC_TENANT_ID
  - FABRIC_CLIENT_ID
  - FABRIC_CLIENT_SECRET

## Instructions

### 1. Display Test Starting Message
Show what will be tested:

```
🔍 Testing Microsoft Fabric API Connection

This will verify:
  ✓ Environment variables are set
  ✓ Credentials are valid
  ✓ Token can be acquired from Microsoft Entra ID
  ✓ Fabric API is accessible
  ✓ Service principal has necessary permissions

Starting tests...
```

### 2. Validate Environment Variables
Check that all required credentials are configured:

```bash
echo ""
echo "📋 Step 1/5: Checking environment variables..."

missing_vars=()

if [ -z "$FABRIC_TENANT_ID" ]; then
  missing_vars+=("FABRIC_TENANT_ID")
fi

if [ -z "$FABRIC_CLIENT_ID" ]; then
  missing_vars+=("FABRIC_CLIENT_ID")
fi

if [ -z "$FABRIC_CLIENT_SECRET" ]; then
  missing_vars+=("FABRIC_CLIENT_SECRET")
fi

if [ ${#missing_vars[@]} -gt 0 ]; then
  echo "❌ Missing environment variables:"
  for var in "${missing_vars[@]}"; do
    echo "  • $var"
  done
  echo ""
  echo "Run /fabric:configure to set up credentials"
  exit 1
fi

echo "✅ All environment variables are set"

# Display masked values for verification
echo "  • FABRIC_TENANT_ID: ${FABRIC_TENANT_ID:0:8}...${FABRIC_TENANT_ID: -4}"
echo "  • FABRIC_CLIENT_ID: ${FABRIC_CLIENT_ID:0:8}...${FABRIC_CLIENT_ID: -4}"
echo "  • FABRIC_CLIENT_SECRET: ${FABRIC_CLIENT_SECRET:0:4}************************"
```

### 3. Validate Credential Formats
Check that credentials are in the correct format:

```bash
echo ""
echo "📋 Step 2/5: Validating credential formats..."

# Validate Tenant ID is a GUID
if ! [[ "$FABRIC_TENANT_ID" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ FABRIC_TENANT_ID is not a valid GUID format"
  echo "  Expected: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  echo "  Got: $FABRIC_TENANT_ID"
  exit 1
fi

# Validate Client ID is a GUID
if ! [[ "$FABRIC_CLIENT_ID" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ FABRIC_CLIENT_ID is not a valid GUID format"
  echo "  Expected: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  echo "  Got: $FABRIC_CLIENT_ID"
  exit 1
fi

# Validate Client Secret is not empty and has reasonable length
if [ ${#FABRIC_CLIENT_SECRET} -lt 20 ]; then
  echo "❌ FABRIC_CLIENT_SECRET seems too short (${#FABRIC_CLIENT_SECRET} characters)"
  echo "  Client secrets are typically 32+ characters"
  echo "  Please verify you copied the full secret value"
  exit 1
fi

echo "✅ All credential formats are valid"
```

### 4. Acquire Access Token
Use the fabric-auth skill to get an access token:

```bash
echo ""
echo "📋 Step 3/5: Acquiring access token from Microsoft Entra ID..."
echo "  Endpoint: https://login.microsoftonline.com/${FABRIC_TENANT_ID:0:8}.../oauth2/v2.0/token"

# Measure token acquisition time
start_time=$(date +%s%3N)

# Make token request
token_response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://login.microsoftonline.com/$FABRIC_TENANT_ID/oauth2/v2.0/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=$FABRIC_CLIENT_ID" \
  -d "client_secret=$FABRIC_CLIENT_SECRET" \
  -d "scope=https://api.fabric.microsoft.com/.default")

end_time=$(date +%s%3N)
duration=$((end_time - start_time))

# Split response and status code
http_code=$(echo "$token_response" | tail -n1)
response_body=$(echo "$token_response" | head -n-1)

if [ "$http_code" != "200" ]; then
  echo "❌ Failed to acquire token (HTTP $http_code)"
  echo ""

  # Parse error details
  error_code=$(echo "$response_body" | jq -r '.error // "Unknown"')
  error_desc=$(echo "$response_body" | jq -r '.error_description // "No description"')

  echo "Error: $error_code"
  echo "Description: $error_desc"
  echo ""

  case "$error_code" in
    "invalid_client")
      echo "Possible causes:"
      echo "  • Client ID is incorrect"
      echo "  • Client secret is incorrect or expired"
      echo "  • Service principal doesn't exist"
      echo ""
      echo "Actions:"
      echo "  • Verify credentials in Azure Portal"
      echo "  • Check if client secret has expired"
      echo "  • Run /fabric:configure to update credentials"
      ;;
    "unauthorized_client")
      echo "Possible causes:"
      echo "  • Service principal doesn't have permission to access Fabric API"
      echo "  • API permissions not granted"
      echo ""
      echo "Actions:"
      echo "  • Azure Portal → App registrations → API permissions"
      echo "  • Add required Fabric/Power BI API permissions"
      echo "  • Grant admin consent"
      ;;
    *)
      echo "Actions:"
      echo "  • Check Azure service status"
      echo "  • Verify Tenant ID is correct"
      echo "  • Review error description above"
      ;;
  esac

  exit 1
fi

# Extract token
access_token=$(echo "$response_body" | jq -r '.access_token')
token_type=$(echo "$response_body" | jq -r '.token_type')
expires_in=$(echo "$response_body" | jq -r '.expires_in')

if [ -z "$access_token" ] || [ "$access_token" = "null" ]; then
  echo "❌ Token response missing access_token field"
  exit 1
fi

echo "✅ Access token acquired successfully (${duration}ms)"
echo "  • Token type: $token_type"
echo "  • Expires in: $expires_in seconds ($(($expires_in / 60)) minutes)"

if [ "$verbose" = "true" ]; then
  echo "  • Token (first 20 chars): ${access_token:0:20}..."
  echo "  • Token length: ${#access_token} characters"
fi
```

### 5. Test Fabric API Access
Make a simple API call to verify access:

```bash
echo ""
echo "📋 Step 4/5: Testing Fabric API access..."
echo "  Endpoint: GET https://api.fabric.microsoft.com/v1/workspaces"

start_time=$(date +%s%3N)

# Make test API call - list workspaces (lightweight operation)
api_response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces" \
  -H "Authorization: Bearer $access_token" \
  -H "Content-Type: application/json")

end_time=$(date +%s%3N)
api_duration=$((end_time - start_time))

http_code=$(echo "$api_response" | tail -n1)
response_body=$(echo "$api_response" | head -n-1)

if [ "$http_code" != "200" ]; then
  echo "❌ Fabric API request failed (HTTP $http_code)"
  echo ""

  # Parse error details
  error_code=$(echo "$response_body" | jq -r '.error.code // "Unknown"')
  error_msg=$(echo "$response_body" | jq -r '.error.message // "No message"')

  echo "Error: $error_code"
  echo "Message: $error_msg"
  echo ""

  case "$http_code" in
    "401")
      echo "Authentication failed. Possible causes:"
      echo "  • Token is invalid or malformed"
      echo "  • Token has already expired"
      echo "  • Service principal not enabled in Fabric"
      echo ""
      echo "Actions:"
      echo "  • Verify service principal is enabled in Fabric Admin Portal"
      echo "  • Tenant settings → 'Service principals can use Fabric APIs'"
      ;;
    "403")
      echo "Authorization failed. Possible causes:"
      echo "  • Service principal not enabled for Fabric APIs"
      echo "  • Service principal not added to any workspaces"
      echo "  • Insufficient permissions"
      echo ""
      echo "Actions:"
      echo "  • Enable service principal in Fabric Admin Portal"
      echo "  • Add service principal to at least one workspace"
      echo "  • Wait 15 minutes after enabling for changes to propagate"
      ;;
    "429")
      echo "Rate limited. This is usually temporary."
      echo "  • Wait a few minutes and try again"
      ;;
    "500"|"502"|"503"|"504")
      echo "Fabric service error. This may be temporary."
      echo "  • Check Fabric service status"
      echo "  • Try again in a few minutes"
      ;;
    *)
      echo "Unexpected error. Please check:"
      echo "  • Fabric service status"
      echo "  • Network connectivity"
      echo "  • Firewall/proxy settings"
      ;;
  esac

  exit 1
fi

# Parse successful response
workspace_count=$(echo "$response_body" | jq '.value | length')

echo "✅ Fabric API access successful (${api_duration}ms)"
echo "  • Response time: ${api_duration}ms"
echo "  • Workspaces found: $workspace_count"

if [ "$verbose" = "true" ]; then
  echo "  • Response size: $(echo "$response_body" | wc -c) bytes"
  continuation_token=$(echo "$response_body" | jq -r '.continuationToken // "none"')
  echo "  • Pagination: $continuation_token"
fi
```

### 6. Verify Service Principal Permissions
Check that the service principal has access to at least one workspace:

```bash
echo ""
echo "📋 Step 5/5: Verifying service principal permissions..."

if [ "$workspace_count" -eq 0 ]; then
  echo "⚠️  No workspaces found"
  echo ""
  echo "The service principal is authenticated but has no workspace access."
  echo ""
  echo "Actions:"
  echo "  1. Add service principal to a workspace:"
  echo "     • Open workspace in Fabric portal"
  echo "     • Settings → Manage access"
  echo "     • Add your service principal"
  echo "     • Assign role: Admin, Member, or Contributor"
  echo "  2. Or create a new workspace and assign the service principal"
  echo ""
  echo "Note: This is not an error if you haven't set up workspaces yet."
else
  echo "✅ Service principal has access to $workspace_count workspace(s)"

  # Show first few workspace names
  if [ "$verbose" = "true" ] || [ "$workspace_count" -le 5 ]; then
    echo ""
    echo "Accessible workspaces:"
    echo "$response_body" | jq -r '.value[] | "  • \(.displayName) (\(.id))"' | head -5

    if [ "$workspace_count" -gt 5 ]; then
      echo "  • ... and $((workspace_count - 5)) more"
    fi
  fi
fi
```

### 7. Display Success Summary
Show final summary with performance metrics:

```
═══════════════════════════════════════════════════════════

✅ Connection Test Successful!

All checks passed:
  ✓ Environment variables configured
  ✓ Credential formats valid
  ✓ Token acquisition successful (312ms)
  ✓ Fabric API accessible (245ms)
  ✓ Service principal has permissions (12 workspaces)

Performance:
  • Total test duration: 587ms
  • Token acquisition: 312ms
  • API response time: 245ms
  • Network latency: ~30ms

Your Fabric plugin is ready to use! 🚀

Try these commands:
  • /fabric:list-workspaces
  • /fabric:get-workspace <workspace-id>
  • /fabric:help

═══════════════════════════════════════════════════════════
```

## Error Scenarios

### Scenario 1: Missing Environment Variables
```
🔍 Testing Microsoft Fabric API Connection
...

📋 Step 1/5: Checking environment variables...
❌ Missing environment variables:
  • FABRIC_TENANT_ID
  • FABRIC_CLIENT_ID
  • FABRIC_CLIENT_SECRET

Run /fabric:configure to set up credentials
```

### Scenario 2: Invalid Token Response
```
📋 Step 3/5: Acquiring access token...
❌ Failed to acquire token (HTTP 400)

Error: invalid_client
Description: AADSTS7000215: Invalid client secret provided

Possible causes:
  • Client ID is incorrect
  • Client secret is incorrect or expired
  • Service principal doesn't exist

Actions:
  • Verify credentials in Azure Portal
  • Check if client secret has expired
  • Run /fabric:configure to update credentials
```

### Scenario 3: Service Principal Not Enabled
```
📋 Step 4/5: Testing Fabric API access...
❌ Fabric API request failed (HTTP 403)

Error: Forbidden
Message: Service principal access is not enabled

Authorization failed. Possible causes:
  • Service principal not enabled for Fabric APIs

Actions:
  • Enable service principal in Fabric Admin Portal
  • Tenant settings → 'Service principals can use Fabric APIs'
  • Wait 15 minutes after enabling for changes to propagate
```

### Scenario 4: No Workspace Access
```
📋 Step 5/5: Verifying service principal permissions...
⚠️  No workspaces found

The service principal is authenticated but has no workspace access.

Actions:
  1. Add service principal to a workspace
  2. Or create a new workspace and assign the service principal

Note: This is not an error if you haven't set up workspaces yet.

✅ Connection test partially successful
(Authentication works, but no workspace access)
```

## Verbose Output

When `--verbose` flag is used, display additional diagnostic information:

```
/fabric:test-connection --verbose

...

📋 Step 3/5: Acquiring access token...
  Endpoint: https://login.microsoftonline.com/12345678.../oauth2/v2.0/token
  Request body: grant_type=client_credentials&client_id=...&scope=...

✅ Access token acquired successfully (312ms)
  • Token type: Bearer
  • Expires in: 3599 seconds (59 minutes)
  • Token (first 20 chars): eyJ0eXAiOiJKV1QiLCJh...
  • Token length: 1847 characters
  • Token claims:
    - aud: https://api.fabric.microsoft.com
    - iss: https://sts.windows.net/...
    - appid: 87654321-4321-4321-4321-cba987654321
    - exp: 1699999999

📋 Step 4/5: Testing Fabric API access...
  Endpoint: GET https://api.fabric.microsoft.com/v1/workspaces
  Request headers:
    - Authorization: Bearer eyJ0eXA...
    - Content-Type: application/json

✅ Fabric API access successful (245ms)
  • Response time: 245ms
  • Response size: 8347 bytes
  • Workspaces found: 12
  • Pagination: none
  • Response headers:
    - x-ms-request-id: abc-123-def
    - x-ms-correlation-id: xyz-789-uvw

...
```

## Performance Benchmarks

Typical test durations:
- **Fast**: <500ms total (good network, nearby region)
- **Normal**: 500-1000ms total
- **Slow**: 1000-2000ms total (far region, slow network)
- **Very slow**: >2000ms (potential network issues)

If test takes >3000ms, display warning:
```
⚠️  Test completed but took longer than expected (3247ms)

This may indicate:
  • Slow network connection
  • High latency to Azure region
  • Microsoft services under load

If this persists, check:
  • Network connectivity
  • Azure service status
  • Consider using different Azure region if possible
```

## Related Commands
- `/fabric:configure` - Set up credentials
- `/fabric:list-workspaces` - List accessible workspaces
- `/fabric:help` - Get help with commands

## Testing Checklist
- [ ] Valid credentials → All tests pass
- [ ] Missing env vars → Clear error with setup instructions
- [ ] Invalid tenant ID format → Format validation error
- [ ] Wrong client secret → Authentication error with cause
- [ ] Service principal not enabled → 403 error with setup instructions
- [ ] No workspace access → Warning but not failure
- [ ] Network timeout → Retry logic and clear error
- [ ] --verbose flag → Additional diagnostic output displayed
- [ ] Performance metrics displayed → Duration for each step
