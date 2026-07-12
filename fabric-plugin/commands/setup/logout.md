---
description: Sign out and clear Fabric API authentication
argument-hint: [--all]
---

# /fabric-plugin:setup:logout

## Purpose

Sign out from Microsoft Fabric API by removing all cached authentication credentials. This includes access tokens, refresh tokens, and any cached authentication data. After logout, you'll need to re-authenticate with `/fabric-plugin:setup:login` or `/fabric-plugin:setup:configure`.

## Arguments

- `--all` (optional): Clear all authentication data including environment variables

## Prerequisites

None - works even if not currently authenticated

## Instructions

### 1. Input Validation

```bash
clear_env=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)
      clear_env=true
      shift
      ;;
    *)
      echo "❌ Unknown argument: $1"
      echo "Usage: /fabric-plugin:setup:logout [--all]"
      exit 1
      ;;
  esac
done
```

### 2. Determine Cache Locations

```bash
# Plugin cache directory (matches skills/_shared/token_manager.py)
CACHE_DIR="${FABRIC_PLUGIN_CACHE_DIR:-$HOME/.fabric-plugin}"
# Legacy location used by plugin versions < 0.5.0
LEGACY_CACHE_DIR="${TEMP:-/tmp}"

echo "Clearing cached credentials..."
echo ""
```

### 3. Clear Cached Tokens

```bash
# Find and remove all token files
token_files_removed=0

# Access tokens (various patterns)
for pattern in \
  "${CACHE_DIR}/fabric-plugin-token-*.json" \
  "${LEGACY_CACHE_DIR}/fabric-plugin-token-*.json"; do

  for file in $pattern; do
    if [ -f "$file" ]; then
      rm -f "$file"
      echo "✅ Removed: $(basename "$file")"
      token_files_removed=$((token_files_removed + 1))
    fi
  done
done

# Refresh tokens
for file in \
  "${CACHE_DIR}/fabric-plugin-refresh-token.json" \
  "${LEGACY_CACHE_DIR}/fabric-plugin-refresh-token.json"; do

  if [ -f "$file" ]; then
    rm -f "$file"
    echo "✅ Removed: $(basename "$file")"
    token_files_removed=$((token_files_removed + 1))
  fi
done

# PKCE temporary files
for file in \
  "${CACHE_DIR}/fabric-auth-code.txt" \
  "${LEGACY_CACHE_DIR}/fabric-auth-code.txt"; do

  if [ -f "$file" ]; then
    rm -f "$file"
    token_files_removed=$((token_files_removed + 1))
  fi
done

if [ $token_files_removed -eq 0 ]; then
  echo "ℹ️  No cached credentials found (already logged out)"
else
  echo ""
  echo "✅ Cleared $token_files_removed credential file(s)"
fi
```

### 4. Clear Environment Variables (if --all flag)

```bash
if [ "$clear_env" = true ]; then
  echo ""
  echo "Clearing environment variables..."

  # Unset Fabric credentials
  if [ -n "$FABRIC_TENANT_ID" ]; then
    unset FABRIC_TENANT_ID
    echo "✅ Cleared: FABRIC_TENANT_ID"
  fi

  if [ -n "$FABRIC_CLIENT_ID" ]; then
    unset FABRIC_CLIENT_ID
    echo "✅ Cleared: FABRIC_CLIENT_ID"
  fi

  if [ -n "$FABRIC_CLIENT_SECRET" ]; then
    unset FABRIC_CLIENT_SECRET
    echo "✅ Cleared: FABRIC_CLIENT_SECRET"
  fi

  if [ -n "$FABRIC_AUTH_FLOW" ]; then
    unset FABRIC_AUTH_FLOW
    echo "✅ Cleared: FABRIC_AUTH_FLOW"
  fi

  echo ""
  echo "⚠️  Note: Environment variables are only cleared for this session."
  echo "    If they're set in your .bashrc or profile, they'll reload on next session."
fi
```

### 5. Display Completion Message

```bash
echo ""
echo "════════════════════════════════════════════════════════"
echo "  ✅ Logout Complete"
echo "════════════════════════════════════════════════════════"
echo ""
echo "What was cleared:"
if [ $token_files_removed -gt 0 ]; then
  echo "  ✓ Cached access tokens"
  echo "  ✓ Cached refresh tokens"
  echo "  ✓ Temporary authentication files"
fi

if [ "$clear_env" = true ]; then
  echo "  ✓ Environment variables (this session only)"
fi

echo ""
echo "To authenticate again:"
echo "  /fabric-plugin:setup:login          (for Microsoft account)"
echo "  /fabric-plugin:setup:configure      (for service principal)"
echo ""
```

## Error Scenarios

This command has no error scenarios - it always succeeds even if no credentials exist.

## Example Usage

```bash
# Basic logout (clear cached tokens)
/fabric-plugin:setup:logout

# Full logout (clear tokens and environment variables)
/fabric-plugin:setup:logout --all
```

## Related Commands

- `/fabric-plugin:setup:login` - Sign in with Microsoft account
- `/fabric-plugin:setup:configure` - Configure service principal credentials
- `/fabric-plugin:setup:test-connection` - Test authentication after re-login
