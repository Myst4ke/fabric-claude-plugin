---
name: fabric-login
description: Authenticate with Microsoft Fabric using OAuth 2.0 delegated flow. This skill should be used when the user needs to sign in with their Microsoft account for Fabric API access.
---

# Fabric Login Skill

Microsoft Fabric authentication using OAuth 2.0 delegated flow with PKCE security.

## When to Use

- User invokes `/fabric-plugin:setup:login`
- Authentication required for Fabric API
- User needs to sign in with Microsoft account

## Instructions

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/fabric-login/authenticate.py"
```

**Do NOT describe. Execute the bash code above immediately using the Bash tool.**

The script will:
- Open browser for OAuth authentication
- Handle callback automatically
- Save access and refresh tokens
- Verify API access
