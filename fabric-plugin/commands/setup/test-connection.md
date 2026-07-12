---
description: Test Microsoft Fabric API connectivity and authentication
argument-hint: [--verbose]
---

# /fabric-plugin:setup:test-connection

## Purpose

Test your Microsoft Fabric API connectivity and authentication configuration. This command verifies that your credentials are valid, the API is accessible, and you have the necessary permissions. It provides diagnostic information helpful for troubleshooting connection issues.

## Arguments

- `--verbose` (optional): Show detailed connection information and diagnostic data

## Prerequisites

- Authenticated with `/fabric-plugin:setup:login` OR `/fabric-plugin:setup:configure`
- Valid cached tokens OR valid environment variables

## Instructions

### 1. Input Validation

```bash
verbose=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --verbose)
      verbose=true
      shift
      ;;
    *)
      echo "❌ Unknown argument: $1"
      echo "Usage: /fabric-plugin:setup:test-connection [--verbose]"
      exit 1
      ;;
  esac
done

echo "════════════════════════════════════════════════════════"
echo "  Testing Fabric API Connection"
echo "════════════════════════════════════════════════════════"
echo ""
```

### 2. Check Authentication Configuration

```bash
# Check for cached tokens
CACHE_DIR="${FABRIC_PLUGIN_CACHE_DIR:-$HOME/.fabric-plugin}"
ACCESS_TOKEN_FILE="${CACHE_DIR}/fabric-plugin-token-delegated.json"
SP_TOKEN_FILE="${CACHE_DIR}/fabric-plugin-token-${FABRIC_CLIENT_ID}.json"

auth_method="Unknown"

if [ -f "$ACCESS_TOKEN_FILE" ]; then
  auth_method="Delegated (Microsoft Account)"
  echo "✅ Found cached delegated auth token"
elif [ -f "$SP_TOKEN_FILE" ]; then
  auth_method="Service Principal"
  echo "✅ Found cached service principal token"
elif [ -n "$FABRIC_CLIENT_ID" ] && [ -n "$FABRIC_CLIENT_SECRET" ]; then
  auth_method="Service Principal (not cached)"
  echo "ℹ️  Service principal credentials configured"
else
  echo "❌ No authentication found"
  echo ""
  echo "Please authenticate first:"
  echo "  /fabric-plugin:setup:login          (for Microsoft account)"
  echo "  /fabric-plugin:setup:configure      (for service principal)"
  exit 1
fi

if [ "$verbose" = true ]; then
  echo "   Authentication method: $auth_method"
fi

echo ""
```

### 3. Obtain Access Token

Use the fabric-auth skill to get a valid token:

```bash
echo "🔐 Authenticating..."

# Determine cache file based on auth method
if [ "$auth_method" = "Delegated (Microsoft Account)" ]; then
  # Check for cached delegated token
  if [ -f "$ACCESS_TOKEN_FILE" ]; then
    expires_at=$(bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" -c "import json,sys; print(json.load(sys.stdin).get('expires_at') or 0)" < "$ACCESS_TOKEN_FILE" 2>/dev/null)
    current_time=$(date +%s)

    if [ "$expires_at" -gt "$current_time" ]; then
      access_token=$(bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" -c "import json,sys; print(json.load(sys.stdin).get('access_token') or 'null')" < "$ACCESS_TOKEN_FILE")
      echo "   Using cached delegated token"
    else
      # Try refresh token
      REFRESH_TOKEN_FILE="${CACHE_DIR}/fabric-plugin-refresh-token.json"
      if [ -f "$REFRESH_TOKEN_FILE" ]; then
        echo "   Token expired, refreshing..."
        # Refresh logic would go here (or redirect to login)
        echo "   Please run: /fabric-plugin:setup:login"
        exit 1
      fi
    fi
  fi
else
  # Service principal - would use fabric-auth skill
  echo "   Acquiring service principal token..."
  echo "   ℹ️  Note: Service principal auth not fully implemented yet"
  echo "   Please use delegated auth: /fabric-plugin:setup:login"
  exit 1
fi

if [ -z "$access_token" ] || [ "$access_token" = "null" ]; then
  echo "❌ Failed to get access token"
  echo ""
  echo "Please authenticate:"
  echo "  /fabric-plugin:setup:login"
  exit 1
fi

echo "✅ Token obtained"
echo ""
```

### 4. Test API Connection

Make a minimal API call to verify connectivity:

```bash
echo "🌐 Testing Fabric API..."

start_time=$(date +%s%3N 2>/dev/null || date +%s)

response=$(curl -s -w "\n%{http_code}" --max-time 10 -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces?\$top=1" \
  -H "Authorization: Bearer $access_token" \
  -H "Content-Type: application/json")

end_time=$(date +%s%3N 2>/dev/null || date +%s)
response_time=$((end_time - start_time))

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
  echo "✅ API accessible (HTTP 200)"

  # Calculate response time (milliseconds if available, seconds otherwise)
  if [ "$response_time" -lt 10000 ]; then
    echo "   Response time: ${response_time}ms"
  else
    echo "   Response time: $((response_time / 1000))s"
  fi

else
  echo "❌ API request failed (HTTP $http_code)"
  echo ""

  # Parse error
  error_code=$(echo "$body" | bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" -c "import json,sys; print((json.load(sys.stdin).get('error') or {}).get('code') or 'Unknown')" 2>/dev/null || echo "Unknown")
  error_message=$(echo "$body" | bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" -c "import json,sys; print((json.load(sys.stdin).get('error') or {}).get('message') or 'No details')" 2>/dev/null || echo "No details")

  echo "Error: $error_code"
  echo "Details: $error_message"
  echo ""

  # Provide guidance based on error
  case "$http_code" in
    401)
      echo "💡 Token is invalid or expired"
      echo "   Run: /fabric-plugin:setup:login"
      ;;
    403)
      echo "💡 Insufficient permissions"
      echo "   Your account may not have Fabric access"
      echo "   Check you have a Fabric license or trial"
      ;;
    *)
      echo "💡 Check Fabric service status or network connection"
      ;;
  esac

  exit 1
fi
```

### 5. Get User Information (Verbose Mode)

```bash
if [ "$verbose" = true ]; then
  echo ""
  echo "Fetching account information..."

  # Get workspace count
  workspace_count=$(echo "$body" | bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" -c "import json,sys; print(len(json.load(sys.stdin).get('value', [])))" 2>/dev/null || echo "0")

  echo "   Available workspaces: $workspace_count"

  # Could add more diagnostic info
  echo "   API base URL: https://api.fabric.microsoft.com/v1"
  echo "   Token type: Bearer"

  # Token info (without revealing token)
  token_length=${#access_token}
  echo "   Token length: $token_length characters"

  if [ -f "$ACCESS_TOKEN_FILE" ]; then
    cached_at=$(bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" -c "import json,sys; print(json.load(sys.stdin).get('cached_at') or 'null')" < "$ACCESS_TOKEN_FILE" 2>/dev/null)
    if [ "$cached_at" != "null" ]; then
      cached_date=$(date -d "@$cached_at" 2>/dev/null || date -r "$cached_at" 2>/dev/null || echo "Unknown")
      echo "   Token cached: $cached_date"
    fi

    expires_at=$(bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" -c "import json,sys; print(json.load(sys.stdin).get('expires_at') or 0)" < "$ACCESS_TOKEN_FILE" 2>/dev/null)
    time_remaining=$((expires_at - $(date +%s)))
    echo "   Token expires in: $((time_remaining / 60)) minutes"
  fi
fi
```

### 6. Display Success Summary

```bash
echo ""
echo "════════════════════════════════════════════════════════"
echo "  ✅ Connection Test Successful"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Your Fabric API connection is working correctly!"
echo ""
echo "Try asking Claude to:"
echo "  List your workspaces        (fabric-plugin:workspace-list skill)"
echo "  Get workspace details       (fabric-plugin:workspace-get skill)"
echo ""
```

## Error Scenarios

- **No authentication found**: Prompt to run `/fabric-plugin:setup:login` or `/fabric-plugin:setup:configure`
- **HTTP 401**: Token invalid/expired, suggest re-login
- **HTTP 403**: Insufficient permissions, check Fabric license
- **Network timeout**: Connection issues, check network
- **HTTP 500**: Fabric service issues, try again later

## Example Usage

```bash
# Basic connection test
/fabric-plugin:setup:test-connection

# Verbose test with detailed diagnostics
/fabric-plugin:setup:test-connection --verbose
```

## Related Commands

- `/fabric-plugin:setup:login` - Authenticate if test fails
- `/fabric-plugin:setup:configure` - Configure service principal
- `/fabric-plugin:setup:logout` - Sign out
- `fabric-plugin:workspace-list` skill - Try after successful test (ask Claude to list your workspaces)
