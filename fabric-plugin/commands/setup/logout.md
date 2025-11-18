---
description: Sign out and clear Fabric API authentication
argument-hint: [--all]
---

# /fabric:logout

## Purpose
Sign out from Microsoft Fabric API by clearing stored authentication tokens. This command removes cached tokens and optionally clears service principal credentials.

## Arguments
- `--all`: Optional. Also clear service principal environment variables (requires shell restart)

## Prerequisites
None (can be run anytime)

## Instructions

### 1. Display Current Authentication Status

```bash
echo "🔓 Microsoft Fabric - Sign Out"
echo ""

AUTH_TYPE="${FABRIC_AUTH_TYPE:-service_principal}"
TOKEN_CACHE="$HOME/.fabric/token_cache.json"
SP_TOKEN_CACHE="/tmp/fabric_token_cache_sp.json"

# Check what's currently authenticated
if [ "$AUTH_TYPE" = "delegated" ]; then
  if [ -f "$TOKEN_CACHE" ]; then
    EXPIRES_AT=$(jq -r '.expires_at' "$TOKEN_CACHE" 2>/dev/null)
    if [ -n "$EXPIRES_AT" ] && [ "$EXPIRES_AT" != "null" ]; then
      echo "Current authentication:"
      echo "  • Type: Delegated (user account)"
      echo "  • Token expires: $(date -d @$EXPIRES_AT '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date -r $EXPIRES_AT '+%Y-%m-%d %H:%M:%S' 2>/dev/null || echo 'Unknown')"
      echo "  • Cache location: ~/.fabric/token_cache.json"
    fi
  else
    echo "ℹ️  No active user authentication found"
  fi
elif [ "$AUTH_TYPE" = "service_principal" ]; then
  if [ -n "$FABRIC_TENANT_ID" ] && [ -n "$FABRIC_CLIENT_ID" ]; then
    echo "Current authentication:"
    echo "  • Type: Service Principal"
    echo "  • Tenant ID: ${FABRIC_TENANT_ID:0:8}...${FABRIC_TENANT_ID: -4}"
    echo "  • Client ID: ${FABRIC_CLIENT_ID:0:8}...${FABRIC_CLIENT_ID: -4}"
    if [ -f "$SP_TOKEN_CACHE" ]; then
      echo "  • Cached token: Yes"
    fi
  else
    echo "ℹ️  No active service principal authentication found"
  fi
fi

echo ""
```

### 2. Confirm Sign Out

```bash
if [ "$all_flag" = "true" ]; then
  echo "⚠️  Warning: --all flag will clear ALL authentication"
  echo ""
  echo "This will:"
  echo "  • Clear delegated user tokens"
  echo "  • Clear service principal token cache"
  echo "  • Remove FABRIC_* environment variables from shell config"
  echo ""
  echo "Are you sure you want to proceed? (y/n)"
else
  echo "This will clear your current authentication."
  echo ""
  echo "Continue? (y/n)"
fi

read -r response

if [ "$response" != "y" ] && [ "$response" != "Y" ]; then
  echo "❌ Sign out canceled"
  exit 0
fi

echo ""
```

### 3. Clear Delegated User Tokens

```bash
if [ -f "$TOKEN_CACHE" ]; then
  echo "🗑️  Clearing user authentication tokens..."

  # Remove token cache
  rm -f "$TOKEN_CACHE"

  if [ ! -f "$TOKEN_CACHE" ]; then
    echo "✅ User tokens cleared"
  else
    echo "❌ Failed to clear user tokens (permission denied?)"
  fi
else
  echo "ℹ️  No user tokens to clear"
fi
```

### 4. Clear Service Principal Token Cache

```bash
if [ -f "$SP_TOKEN_CACHE" ]; then
  echo "🗑️  Clearing service principal token cache..."

  rm -f "$SP_TOKEN_CACHE"

  if [ ! -f "$SP_TOKEN_CACHE" ]; then
    echo "✅ Service principal cache cleared"
  else
    echo "❌ Failed to clear cache (permission denied?)"
  fi
fi

# Also check Windows temp location
if [ -f "%TEMP%\\fabric_token_cache_sp.json" ]; then
  rm -f "%TEMP%\\fabric_token_cache_sp.json"
fi
```

### 5. Clear Environment Variables (if --all flag)

```bash
if [ "$all_flag" = "true" ]; then
  echo ""
  echo "🗑️  Clearing environment variables..."

  # Unset for current session
  unset FABRIC_TENANT_ID
  unset FABRIC_CLIENT_ID
  unset FABRIC_CLIENT_SECRET
  unset FABRIC_AUTH_TYPE

  echo "✅ Environment variables unset for current session"

  # Find and update shell config file
  config_files=(
    "$HOME/.zshrc"
    "$HOME/.bashrc"
    "$HOME/.bash_profile"
    "$HOME/.profile"
  )

  for config_file in "${config_files[@]}"; do
    if [ -f "$config_file" ]; then
      # Check if FABRIC variables exist in file
      if grep -q "FABRIC_TENANT_ID\|FABRIC_CLIENT_ID\|FABRIC_CLIENT_SECRET\|FABRIC_AUTH_TYPE" "$config_file"; then
        echo ""
        echo "Found Fabric credentials in: $config_file"
        echo "Do you want to remove them? (y/n)"
        read -r remove_response

        if [ "$remove_response" = "y" ] || [ "$remove_response" = "Y" ]; then
          # Create backup
          cp "$config_file" "${config_file}.backup.$(date +%Y%m%d_%H%M%S)"
          echo "✅ Backup created: ${config_file}.backup.$(date +%Y%m%d_%H%M%S)"

          # Remove FABRIC lines
          sed -i.tmp '/FABRIC_TENANT_ID/d' "$config_file"
          sed -i.tmp '/FABRIC_CLIENT_ID/d' "$config_file"
          sed -i.tmp '/FABRIC_CLIENT_SECRET/d' "$config_file"
          sed -i.tmp '/FABRIC_AUTH_TYPE/d' "$config_file"
          sed -i.tmp '/# Microsoft Fabric API Credentials/d' "$config_file"
          rm -f "${config_file}.tmp"

          echo "✅ Credentials removed from: $config_file"
          echo "   (Backup saved in case you need to restore)"
        fi
      fi
    fi
  done

  echo ""
  echo "⚠️  Important: Restart your terminal for changes to take effect"
  echo "   Or run: source ~/.zshrc (or your shell config file)"
fi
```

### 6. Display Success Message

```bash
echo ""
echo "✅ Sign Out Complete"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Successfully signed out from Microsoft Fabric"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$all_flag" = "true" ]; then
  echo "All authentication cleared:"
  echo "  ✓ User tokens removed"
  echo "  ✓ Service principal cache cleared"
  echo "  ✓ Environment variables unset"
  echo ""
  echo "To authenticate again:"
  echo "  • User authentication: /fabric\\:login"
  echo "  • Service principal: /fabric\\:configure"
else
  echo "Current session authentication cleared:"
  echo "  ✓ Tokens removed"
  echo "  ✓ Cache cleared"
  echo ""
  echo "To sign in again:"
  if [ "$AUTH_TYPE" = "delegated" ]; then
    echo "  • /fabric\\:login (user account)"
    echo "  • /fabric\\:configure (service principal)"
  else
    echo "  • /fabric\\:configure (service principal)"
    echo "  • /fabric\\:login (user account)"
  fi
fi

echo ""
```

## Error Scenarios

### Scenario 1: Permission Denied
```
❌ Failed to clear tokens

Permission denied when accessing:
  ~/.fabric/token_cache.json

Actions:
  • Check file permissions: ls -l ~/.fabric/token_cache.json
  • Try with elevated permissions if appropriate
  • Manually remove: rm ~/.fabric/token_cache.json
```

### Scenario 2: File Not Found (Already Signed Out)
```
ℹ️  No active authentication found

You are already signed out.

To sign in:
  • User account: /fabric:login
  • Service principal: /fabric:configure
```

### Scenario 3: Backup Failed
```
⚠️  Could not create backup of shell config

Proceeding without backup may cause data loss.

Do you want to continue anyway? (y/n)
```

## Testing Checklist
- [ ] Clears delegated user tokens from ~/.fabric/token_cache.json
- [ ] Clears service principal cache from /tmp
- [ ] With --all flag, removes environment variables from shell config
- [ ] Creates backup before modifying shell config
- [ ] Shows clear success message
- [ ] Handles case when no authentication exists
- [ ] Works on Windows, Mac, and Linux
- [ ] Prompts for confirmation before clearing
- [ ] With --all, warns about clearing everything

## Related Commands
- `/fabric:login` - Sign in with Microsoft account
- `/fabric:configure` - Set up service principal authentication
- `/fabric:test-connection` - Test authentication status

## Example Usage

### Basic Sign Out (Delegated Auth)
```
$ /fabric:logout

🔓 Microsoft Fabric - Sign Out

Current authentication:
  • Type: Delegated (user account)
  • Token expires: 2025-01-18 15:30:00
  • Cache location: ~/.fabric/token_cache.json

This will clear your current authentication.

Continue? (y/n) y

🗑️  Clearing user authentication tokens...
✅ User tokens cleared

✅ Sign Out Complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Successfully signed out from Microsoft Fabric
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Current session authentication cleared:
  ✓ Tokens removed
  ✓ Cache cleared

To sign in again:
  • /fabric\:login (user account)
  • /fabric\:configure (service principal)
```

### Sign Out with --all Flag
```
$ /fabric:logout --all

🔓 Microsoft Fabric - Sign Out

Current authentication:
  • Type: Service Principal
  • Tenant ID: 12345678...9abc
  • Client ID: 87654321...4321
  • Cached token: Yes

⚠️  Warning: --all flag will clear ALL authentication

This will:
  • Clear delegated user tokens
  • Clear service principal token cache
  • Remove FABRIC_* environment variables from shell config

Are you sure you want to proceed? (y/n) y

🗑️  Clearing user authentication tokens...
ℹ️  No user tokens to clear

🗑️  Clearing service principal token cache...
✅ Service principal cache cleared

🗑️  Clearing environment variables...
✅ Environment variables unset for current session

Found Fabric credentials in: /home/user/.zshrc
Do you want to remove them? (y/n) y
✅ Backup created: /home/user/.zshrc.backup.20250118_143000
✅ Credentials removed from: /home/user/.zshrc
   (Backup saved in case you need to restore)

⚠️  Important: Restart your terminal for changes to take effect
   Or run: source ~/.zshrc (or your shell config file)

✅ Sign Out Complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Successfully signed out from Microsoft Fabric
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

All authentication cleared:
  ✓ User tokens removed
  ✓ Service principal cache cleared
  ✓ Environment variables unset

To authenticate again:
  • User authentication: /fabric\:login
  • Service principal: /fabric\:configure
```

### Already Signed Out
```
$ /fabric:logout

🔓 Microsoft Fabric - Sign Out

ℹ️  No active authentication found

You are already signed out.

To sign in:
  • User account: /fabric:login
  • Service principal: /fabric:configure
```
