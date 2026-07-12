---
description: Interactive setup for Fabric API credentials
argument-hint: [--validate]
---

# /fabric-plugin:setup:configure

## Purpose

Interactive setup wizard for configuring Microsoft Fabric API credentials using Azure AD service principal authentication. This command guides you through entering your Azure AD tenant ID, client ID, and client secret, validates the format, tests the connection, and stores credentials for use in all Fabric operations.

## Arguments

- `--validate` (optional): Test existing credentials without reconfiguring

## Prerequisites

For service principal authentication, you need:
- Azure AD app registration with client secret
- Fabric API permissions granted
- Service principal enabled in Fabric Admin Portal

See `docs/AZURE_APP_SETUP.md` for detailed setup instructions.

## Instructions

### 1. Input Validation

```bash
validate_only=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --validate)
      validate_only=true
      shift
      ;;
    *)
      echo "❌ Unknown argument: $1"
      echo "Usage: /fabric-plugin:setup:configure [--validate]"
      exit 1
      ;;
  esac
done

echo "════════════════════════════════════════════════════════"
echo "  Microsoft Fabric API Configuration"
echo "════════════════════════════════════════════════════════"
echo ""
```

### 2. Check Existing Configuration (Validate Mode)

```bash
if [ "$validate_only" = true ]; then
  echo "Validating existing configuration..."
  echo ""

  # Check environment variables
  if [ -z "$FABRIC_TENANT_ID" ]; then
    echo "❌ FABRIC_TENANT_ID not set"
    has_error=true
  else
    echo "✅ FABRIC_TENANT_ID: ${FABRIC_TENANT_ID:0:8}...${FABRIC_TENANT_ID: -8}"
  fi

  if [ -z "$FABRIC_CLIENT_ID" ]; then
    echo "❌ FABRIC_CLIENT_ID not set"
    has_error=true
  else
    echo "✅ FABRIC_CLIENT_ID: ${FABRIC_CLIENT_ID:0:8}...${FABRIC_CLIENT_ID: -8}"
  fi

  if [ -z "$FABRIC_CLIENT_SECRET" ]; then
    echo "❌ FABRIC_CLIENT_SECRET not set"
    has_error=true
  else
    echo "✅ FABRIC_CLIENT_SECRET: (hidden for security)"
  fi

  if [ "$has_error" = true ]; then
    echo ""
    echo "Run without --validate to configure credentials"
    exit 1
  fi

  echo ""
  echo "✅ Configuration valid"
  echo ""
  echo "Testing connection..."
  # Run test-connection command
  /fabric-plugin:setup:test-connection
  exit $?
fi
```

### 3. Display Setup Options

```bash
echo "Choose authentication method:"
echo ""
echo "1. Microsoft Account (Recommended for personal use)"
echo "   - Easy browser-based login"
echo "   - Uses your existing Fabric permissions"
echo "   - No Azure AD setup required"
echo ""
echo "2. Service Principal (For automation/CI/CD)"
echo "   - Requires Azure AD app registration"
echo "   - More complex setup"
echo "   - Better for production systems"
echo ""

read -p "Select option (1 or 2): " auth_option

case "$auth_option" in
  1)
    echo ""
    echo "Redirecting to Microsoft Account login..."
    echo ""
    /fabric-plugin:setup:login
    exit $?
    ;;

  2)
    echo ""
    echo "Service Principal Setup"
    echo "═══════════════════════"
    ;;

  *)
    echo "❌ Invalid option: $auth_option"
    exit 1
    ;;
esac
```

### 4. Collect Credentials (Service Principal)

```bash
echo ""
echo "You'll need these values from Azure Portal:"
echo "  - Tenant ID (Azure AD > Properties)"
echo "  - Client ID (App Registrations > Your App > Overview)"
echo "  - Client Secret (App Registrations > Your App > Certificates & secrets)"
echo ""
echo "See docs/AZURE_APP_SETUP.md for detailed instructions."
echo ""

# Function to validate GUID format
validate_guid() {
  local value="$1"
  if [[ "$value" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
    return 0
  else
    return 1
  fi
}

# Collect Tenant ID
while true; do
  read -p "Enter Tenant ID: " tenant_id

  if validate_guid "$tenant_id"; then
    echo "✅ Tenant ID format valid"
    break
  else
    echo "❌ Invalid format. Should be: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  fi
done

# Collect Client ID
while true; do
  read -p "Enter Client ID: " client_id

  if validate_guid "$client_id"; then
    echo "✅ Client ID format valid"
    break
  else
    echo "❌ Invalid format. Should be: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  fi
done

# Collect Client Secret
while true; do
  read -s -p "Enter Client Secret (hidden): " client_secret
  echo ""

  if [ -z "$client_secret" ]; then
    echo "❌ Client secret cannot be empty"
  else
    echo "✅ Client secret received"
    break
  fi
done
```

### 5. Store Credentials

```bash
echo ""
echo "Storing credentials..."

# Export environment variables for current session
export FABRIC_TENANT_ID="$tenant_id"
export FABRIC_CLIENT_ID="$client_id"
export FABRIC_CLIENT_SECRET="$client_secret"
export FABRIC_AUTH_FLOW="service_principal"

echo "✅ Credentials set for current session"
echo ""
echo "⚠️  Note: These are only set for this session."
echo "    To persist, add to your shell profile (.bashrc, .zshrc, etc.)"
echo ""
```

### 6. Test Credentials

```bash
echo "Testing credentials..."
echo ""

# Acquire token
response=$(curl -s -X POST \
  "https://login.microsoftonline.com/${FABRIC_TENANT_ID}/oauth2/v2.0/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=${FABRIC_CLIENT_ID}" \
  -d "client_secret=${FABRIC_CLIENT_SECRET}" \
  -d "scope=https://api.fabric.microsoft.com/.default")

access_token=$(echo "$response" | bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" -c "import json,sys; print(json.load(sys.stdin).get('access_token') or 'null')")

if [ "$access_token" = "null" ] || [ -z "$access_token" ]; then
  echo "❌ Authentication failed"
  echo ""

  error=$(echo "$response" | bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" -c "import json,sys; print(json.load(sys.stdin).get('error') or 'Unknown')")
  error_desc=$(echo "$response" | bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" -c "import json,sys; print(json.load(sys.stdin).get('error_description') or 'No details')")

  echo "Error: $error"
  echo "Details: $error_desc"
  echo ""
  echo "Common issues:"
  echo "  - Wrong client secret"
  echo "  - Client secret expired"
  echo "  - Missing API permissions"
  echo "  - Service principal not enabled in Fabric"
  echo ""
  echo "See docs/AZURE_APP_SETUP.md for troubleshooting"
  exit 1
fi

echo "✅ Token acquired successfully"

# Test Fabric API
echo "Testing Fabric API access..."

api_response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces?\$top=1" \
  -H "Authorization: Bearer $access_token")

api_http_code=$(echo "$api_response" | tail -n1)

if [ "$api_http_code" = "200" ]; then
  echo "✅ Fabric API accessible"

  workspace_count=$(echo "$api_response" | head -n-1 | bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" -c "import json,sys; print(len(json.load(sys.stdin).get('value', [])))")
  echo "   Available workspaces: $workspace_count"

else
  echo "⚠️  Fabric API returned HTTP $api_http_code"
  echo ""
  echo "This might mean:"
  echo "  - Service principal not enabled in Fabric Admin Portal"
  echo "  - Missing workspace permissions"
  echo "  - Fabric license required"
  echo ""
  echo "See docs/AZURE_APP_SETUP.md for enabling service principal"
fi
```

### 7. Display Completion Message

```bash
echo ""
echo "════════════════════════════════════════════════════════"
echo "  ✅ Configuration Complete"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Service principal authentication is configured!"
echo ""
echo "Environment variables set:"
echo "  FABRIC_TENANT_ID"
echo "  FABRIC_CLIENT_ID"
echo "  FABRIC_CLIENT_SECRET"
echo "  FABRIC_AUTH_FLOW=service_principal"
echo ""
echo "To persist these settings, add to your shell profile:"
echo ""
echo "  export FABRIC_TENANT_ID=\"$tenant_id\""
echo "  export FABRIC_CLIENT_ID=\"$client_id\""
echo "  export FABRIC_CLIENT_SECRET=\"your-secret\""
echo "  export FABRIC_AUTH_FLOW=\"service_principal\""
echo ""
echo "Try asking Claude to list your workspaces"
echo "  (fabric-plugin:workspace-list skill)"
echo ""
```

## Error Scenarios

- **Invalid GUID format**: Re-prompt for correct format
- **Empty client secret**: Re-prompt
- **Authentication fails**: Show error and troubleshooting steps
- **API access fails**: Explain potential causes (permissions, service principal not enabled)
- **Network error**: Suggest checking connection

## Example Usage

```bash
# Interactive setup
/fabric-plugin:setup:configure

# Validate existing credentials
/fabric-plugin:setup:configure --validate
```

## Related Commands

- `/fabric-plugin:setup:login` - Easier alternative (Microsoft account)
- `/fabric-plugin:setup:test-connection` - Test after configuration
- `/fabric-plugin:setup:logout` - Clear credentials
- `/fabric-plugin:setup:help` - Show help information
