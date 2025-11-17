---
description: Interactive setup for Fabric API credentials
argument-hint: [--validate]
---

# /fabric:configure

## Purpose
Interactive command to set up Microsoft Fabric API authentication credentials. This command guides users through configuring their Azure/Entra ID service principal credentials and optionally validates the configuration.

## Arguments
- `--validate`: Optional. Test the credentials immediately after configuration

## Prerequisites
- Azure/Entra ID tenant with Fabric enabled
- Service principal (app registration) created in Azure Portal
- Service principal enabled in Fabric Admin Portal settings

## Instructions

### 1. Display Welcome Message
Show a friendly introduction explaining what this command does:

```
🔧 Microsoft Fabric API Configuration

This wizard will help you configure credentials for accessing the Fabric API.

You'll need:
  • Azure tenant ID
  • Application (client) ID
  • Client secret

Don't have these? See setup guide at the end.
```

### 2. Check Existing Configuration
Check if credentials are already configured:

```bash
if [ -n "$FABRIC_TENANT_ID" ] && [ -n "$FABRIC_CLIENT_ID" ] && [ -n "$FABRIC_CLIENT_SECRET" ]; then
  echo ""
  echo "⚠️ Credentials are already configured:"
  echo "  Tenant ID: ${FABRIC_TENANT_ID:0:8}...${FABRIC_TENANT_ID: -4}"
  echo "  Client ID: ${FABRIC_CLIENT_ID:0:8}...${FABRIC_CLIENT_ID: -4}"
  echo ""
  echo "Do you want to reconfigure? (y/n)"
  read -r response

  if [ "$response" != "y" ] && [ "$response" != "Y" ]; then
    echo "✅ Keeping existing configuration"
    exit 0
  fi
fi
```

### 3. Collect Tenant ID
Prompt for Azure tenant ID with validation:

```bash
echo ""
echo "📋 Step 1/3: Azure Tenant ID"
echo "Format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
echo ""
echo "Where to find this:"
echo "  1. Azure Portal → Azure Active Directory → Overview"
echo "  2. Look for 'Tenant ID' or 'Directory ID'"
echo ""
echo "Enter your Tenant ID:"
read -r tenant_id

# Validate GUID format
if ! [[ "$tenant_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid format. Tenant ID must be a valid GUID."
  echo "Example: 12345678-1234-1234-1234-123456789abc"
  exit 1
fi

echo "✅ Tenant ID validated"
```

### 4. Collect Client ID
Prompt for application (client) ID:

```bash
echo ""
echo "📋 Step 2/3: Application (Client) ID"
echo "Format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
echo ""
echo "Where to find this:"
echo "  1. Azure Portal → Azure Active Directory → App registrations"
echo "  2. Select your application"
echo "  3. Look for 'Application (client) ID' on Overview page"
echo ""
echo "Enter your Client ID:"
read -r client_id

# Validate GUID format
if ! [[ "$client_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid format. Client ID must be a valid GUID."
  exit 1
fi

echo "✅ Client ID validated"
```

### 5. Collect Client Secret
Prompt for client secret with masked input:

```bash
echo ""
echo "📋 Step 3/3: Client Secret"
echo ""
echo "Where to find this:"
echo "  1. Azure Portal → App registrations → Your app"
echo "  2. Go to 'Certificates & secrets'"
echo "  3. Create a 'New client secret' if needed"
echo "  4. Copy the secret VALUE (not the ID)"
echo ""
echo "⚠️  Warning: The secret will not be displayed after creation"
echo ""
echo "Enter your Client Secret (input will be hidden):"
read -s client_secret
echo ""

# Validate not empty
if [ -z "$client_secret" ]; then
  echo "❌ Client secret cannot be empty"
  exit 1
fi

# Validate minimum length (typically 32+ characters)
if [ ${#client_secret} -lt 20 ]; then
  echo "❌ Client secret seems too short. Please verify you copied the full secret."
  exit 1
fi

echo "✅ Client secret validated"
```

### 6. Save Configuration
Save credentials to appropriate location based on OS:

```bash
echo ""
echo "💾 Saving configuration..."

# Determine shell config file
if [ -f "$HOME/.zshrc" ]; then
  config_file="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
  config_file="$HOME/.bashrc"
elif [ -f "$HOME/.bash_profile" ]; then
  config_file="$HOME/.bash_profile"
else
  config_file="$HOME/.profile"
fi

# Check if variables already exist in file
if grep -q "FABRIC_TENANT_ID" "$config_file"; then
  echo ""
  echo "⚠️ Configuration already exists in $config_file"
  echo "Do you want to update it? (y/n)"
  read -r response

  if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
    # Remove old configuration
    sed -i '/FABRIC_TENANT_ID/d' "$config_file"
    sed -i '/FABRIC_CLIENT_ID/d' "$config_file"
    sed -i '/FABRIC_CLIENT_SECRET/d' "$config_file"
  fi
fi

# Append new configuration
cat >> "$config_file" << EOF

# Microsoft Fabric API Credentials (added by /fabric:configure on $(date +%Y-%m-%d))
export FABRIC_TENANT_ID="$tenant_id"
export FABRIC_CLIENT_ID="$client_id"
export FABRIC_CLIENT_SECRET="$client_secret"
EOF

# Set in current session
export FABRIC_TENANT_ID="$tenant_id"
export FABRIC_CLIENT_ID="$client_id"
export FABRIC_CLIENT_SECRET="$client_secret"

echo "✅ Configuration saved to $config_file"
echo "✅ Environment variables set for current session"
```

### 7. Display Success Message
Show completion message with next steps:

```
✅ Configuration Complete!

Your Fabric API credentials have been configured successfully.

Configuration saved to: ~/.zshrc
Variables set:
  ✓ FABRIC_TENANT_ID
  ✓ FABRIC_CLIENT_ID
  ✓ FABRIC_CLIENT_SECRET

Next steps:
  1. Restart your terminal or run: source ~/.zshrc
  2. Test your connection: /fabric:test-connection
  3. List your workspaces: /fabric:list-workspaces

Important notes:
  • Keep your client secret secure
  • Never commit credentials to git
  • Client secrets expire - check Azure Portal periodically
```

### 8. Optional Validation
If `--validate` flag is provided, test the credentials immediately:

```bash
if [ "$validate" = "true" ]; then
  echo ""
  echo "🔍 Validating credentials..."
  echo ""

  # Call fabric:test-connection command
  # This will be handled by invoking the test-connection command
  echo "Running connection test..."

  # The actual validation will be done by /fabric:test-connection
fi
```

## Error Scenarios

### Scenario 1: Invalid GUID Format
```
❌ Invalid format

Tenant ID must be in GUID format:
  xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

Example: 12345678-1234-1234-1234-123456789abc

Please try again.
```

### Scenario 2: Empty Client Secret
```
❌ Client secret cannot be empty

Please copy the full client secret value from Azure Portal:
  1. Azure Portal → App registrations → Your app
  2. Certificates & secrets → Client secrets
  3. Copy the VALUE column (not Secret ID)

The value should be 32+ characters long.
```

### Scenario 3: File Write Permission Error
```
❌ Permission denied

Could not write to configuration file: ~/.zshrc

Actions:
  • Check file permissions: ls -l ~/.zshrc
  • Try with sudo if appropriate
  • Manually add to your shell config:

    export FABRIC_TENANT_ID="{tenant_id}"
    export FABRIC_CLIENT_ID="{client_id}"
    export FABRIC_CLIENT_SECRET="{client_secret}"
```

## Setup Guide for New Users

If user doesn't have service principal yet, display this comprehensive guide:

```
📘 Setting Up Service Principal for Fabric API

Don't have credentials yet? Follow these steps:

STEP 1: Create App Registration in Azure
  1. Go to Azure Portal (portal.azure.com)
  2. Navigate to Azure Active Directory
  3. Click "App registrations" → "New registration"
  4. Name: "Fabric API Access" (or your preferred name)
  5. Supported account types: "Single tenant"
  6. Click "Register"
  7. Copy the "Application (client) ID" - you'll need this
  8. Copy the "Directory (tenant) ID" - you'll need this

STEP 2: Create Client Secret
  1. In your app registration, go to "Certificates & secrets"
  2. Click "New client secret"
  3. Description: "Fabric plugin" (or your preferred name)
  4. Expires: Choose duration (recommended: 12-24 months)
  5. Click "Add"
  6. IMMEDIATELY COPY the secret VALUE - it won't be shown again!

STEP 3: Configure API Permissions
  1. In your app registration, go to "API permissions"
  2. Click "Add a permission"
  3. Select "Power BI Service"
  4. Choose "Delegated permissions" and select:
     • Item.ReadWrite.All
     • Workspace.ReadWrite.All
  5. OR choose "Application permissions" for service principal:
     • Tenant.Read.All
     • Tenant.ReadWrite.All
  6. Click "Add permissions"
  7. Click "Grant admin consent" (requires admin)

STEP 4: Enable Service Principal in Fabric
  1. Go to Fabric Admin Portal (app.fabric.microsoft.com)
  2. Click Settings (gear icon) → Admin portal
  3. Go to "Tenant settings"
  4. Find "Service principals can use Fabric APIs"
  5. Enable the setting
  6. Add your service principal to the allowed list:
     • Security group: Create a group in Azure AD, add the SP
     • OR: Allow for entire organization (less secure)
  7. Click "Apply"
  8. Wait 15 minutes for changes to propagate

STEP 5: Add Service Principal to Workspaces
  For each workspace you want to access:
  1. Open the workspace in Fabric
  2. Click workspace Settings → Manage access
  3. Add your service principal (search by name)
  4. Assign role: Admin, Member, or Contributor
  5. Click "Add"

STEP 6: Run This Configuration Command
  Now you can run /fabric:configure with your credentials!

Troubleshooting:
  • "Unauthorized" errors: Check service principal is enabled in Fabric
  • "Forbidden" errors: Add service principal to workspace
  • "Invalid client": Verify client ID and secret are correct

Documentation:
  • Fabric API Authentication:
    https://learn.microsoft.com/en-us/rest/api/fabric/articles/get-started/fabric-api-quickstart
  • Service Principal Setup:
    https://learn.microsoft.com/en-us/power-bi/developer/embedded/embed-service-principal
```

## Related Commands
- `/fabric:test-connection` - Test configured credentials
- `/fabric:help` - Get help with other commands

## Example Usage

### Basic Configuration
```
/fabric:configure

🔧 Microsoft Fabric API Configuration
...

📋 Step 1/3: Azure Tenant ID
Enter your Tenant ID: 12345678-1234-1234-1234-123456789abc
✅ Tenant ID validated

📋 Step 2/3: Application (Client) ID
Enter your Client ID: 87654321-4321-4321-4321-cba987654321
✅ Client ID validated

📋 Step 3/3: Client Secret
Enter your Client Secret: ****************************************
✅ Client secret validated

💾 Saving configuration...
✅ Configuration saved to ~/.zshrc
✅ Environment variables set for current session

✅ Configuration Complete!
...
```

### Configuration with Validation
```
/fabric:configure --validate

... [configuration steps] ...

✅ Configuration Complete!

🔍 Validating credentials...

Testing connection to Microsoft Fabric API...
✅ Connection successful!
✅ Authentication working correctly

You're all set! Try: /fabric:list-workspaces
```

## Testing Checklist
- [ ] Valid credentials → Saved successfully to shell config
- [ ] Invalid tenant ID format → Clear error message
- [ ] Invalid client ID format → Clear error message
- [ ] Empty client secret → Error with instructions
- [ ] Existing configuration → Prompt to overwrite
- [ ] --validate flag → Runs connection test after setup
- [ ] File permission error → Fallback to manual instructions
- [ ] Setup guide displayed for new users
