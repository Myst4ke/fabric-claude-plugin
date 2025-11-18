---
name: permission-checker
description: Check user permissions and provide graceful error handling for insufficient privileges
---

# Permission Checker Skill

## Purpose
Detect permission-related errors from Fabric API calls and provide clear, actionable feedback to users. This skill helps handle differences between service principal and delegated user authentication, especially when users don't have sufficient privileges for certain operations.

## When to Use
- After receiving 403 Forbidden from Fabric API
- When API returns "InsufficientPrivileges" error
- Before attempting operations that require specific roles
- When switching between authentication methods

## Common Permission Errors

### 1. Insufficient Role in Workspace
**Error Pattern:**
```json
{
  "error": {
    "code": "InsufficientPrivileges",
    "message": "User does not have required permissions"
  }
}
```

**User-Friendly Message:**
```
❌ Permission Denied

This operation requires a higher role in the workspace.

Your current role: Viewer (or Contributor)
Required role: Admin

Actions:
  • Contact the workspace admin to upgrade your role
  • Or use service principal with admin privileges: /fabric:configure

Workspace ID: {workspace_id}
```

### 2. No Access to Workspace
**Error Pattern:**
```json
{
  "error": {
    "code": "WorkspaceNotFound",
    "message": "Workspace not found or access denied"
  }
}
```

**User-Friendly Message:**
```
❌ Access Denied

You don't have access to this workspace.

Actions:
  • Ask the workspace owner to add you: {workspace_id}
  • Check if you're signed in with the correct account
  • Your account: {user_email}

Need to switch accounts? Run: /fabric:logout then /fabric:login
```

### 3. Operation Not Supported for Delegated Auth
**Error Pattern:**
```json
{
  "error": {
    "code": "PrincipalTypeNotSupported",
    "message": "This operation doesn't support user authentication"
  }
}
```

**User-Friendly Message:**
```
❌ Authentication Type Not Supported

This operation requires service principal authentication.
Delegated user authentication is not supported for this API.

To use service principal:
  1. Run: /fabric:logout
  2. Configure service principal: /fabric:configure
  3. Try the operation again

Operation: {operation_name}
```

### 4. Capacity Assignment Requires Higher Privileges
**Error Pattern:**
```
403 Forbidden when trying to assign capacity
```

**User-Friendly Message:**
```
❌ Permission Denied

Assigning workspaces to capacities requires:
  • Workspace Admin role, AND
  • Capacity Contributor or Capacity Admin role

Your current access:
  • Workspace: {workspace_role}
  • Capacity: {capacity_role}

Contact your Fabric administrator for capacity permissions.
```

## Permission Matrix

| Operation | Viewer | Contributor | Member | Admin | Service Principal |
|-----------|--------|-------------|---------|-------|-------------------|
| List items | ✅ | ✅ | ✅ | ✅ | ✅ |
| View item details | ✅ | ✅ | ✅ | ✅ | ✅ |
| Create items | ❌ | ✅ | ✅ | ✅ | ✅ (if allowed) |
| Update items | ❌ | ✅ | ✅ | ✅ | ✅ (if allowed) |
| Delete items | ❌ | ❌ | ✅ | ✅ | ✅ (if allowed) |
| Manage users | ❌ | ❌ | ❌ | ✅ | ✅ (if allowed) |
| Assign capacity | ❌ | ❌ | ❌ | ✅ | ✅ (if allowed) |
| Workspace settings | ❌ | ❌ | ❌ | ✅ | ✅ (if allowed) |

## Implementation

### Detect Permission Error
```bash
# After API call, check response
HTTP_CODE=$(echo "$response" | jq -r '.status_code')
ERROR_CODE=$(echo "$response" | jq -r '.error.code')
ERROR_MSG=$(echo "$response" | jq -r '.error.message')

if [ "$HTTP_CODE" = "403" ] || [ "$ERROR_CODE" = "InsufficientPrivileges" ]; then
  # Handle permission error
  handle_permission_error "$ERROR_CODE" "$ERROR_MSG"
fi
```

### Suggest Alternative Actions
```bash
handle_permission_error() {
  local error_code="$1"
  local error_msg="$2"

  echo "❌ Permission Denied"
  echo ""
  echo "Error: $error_msg"
  echo ""

  # Get current auth type
  AUTH_TYPE="${FABRIC_AUTH_TYPE:-service_principal}"

  if [ "$AUTH_TYPE" = "delegated" ]; then
    echo "You're using delegated (user) authentication."
    echo ""
    echo "Options:"
    echo "  1. Request higher role from workspace admin"
    echo "  2. Switch to service principal: /fabric:configure"
    echo "     (if you have admin access to Azure)"
  else
    echo "You're using service principal authentication."
    echo ""
    echo "Options:"
    echo "  1. Add service principal to workspace with Admin role"
    echo "  2. Grant required permissions in Azure Portal"
  fi
}
```

### Check Role Before Operation
```bash
check_required_role() {
  local required_role="$1"  # Admin, Member, Contributor, Viewer
  local operation="$2"

  # Get current user's role (from previous workspace API call)
  CURRENT_ROLE=$(get_user_role "$WORKSPACE_ID")

  # Role hierarchy: Admin > Member > Contributor > Viewer
  case "$required_role" in
    "Admin")
      if [ "$CURRENT_ROLE" != "Admin" ]; then
        echo "❌ This operation requires Admin role"
        echo "Your role: $CURRENT_ROLE"
        return 1
      fi
      ;;
    "Member")
      if [ "$CURRENT_ROLE" = "Viewer" ] || [ "$CURRENT_ROLE" = "Contributor" ]; then
        echo "❌ This operation requires Member or Admin role"
        echo "Your role: $CURRENT_ROLE"
        return 1
      fi
      ;;
  esac

  return 0
}
```

## Error Message Templates

### Template 1: Insufficient Role
```
❌ Permission Denied

Operation: {operation_name}
Required role: {required_role}
Your role: {current_role}

This operation needs higher privileges in workspace "{workspace_name}".

Actions:
  • Contact workspace admin: {admin_email}
  • Request role upgrade to: {required_role}
  • Or use service principal with proper permissions
```

### Template 2: No Workspace Access
```
❌ Access Denied

You don't have access to workspace: {workspace_name}

Possible reasons:
  • You're not a member of this workspace
  • The workspace was deleted
  • You're signed in with the wrong account

Actions:
  • Ask workspace owner to add you as a member
  • Check your current account: {current_user}
  • Switch accounts: /fabric:logout then /fabric:login
```

### Template 3: Feature Not Available
```
⚠️  Feature Not Available

This operation is not supported with your current authentication.

Authentication type: {auth_type}
Operation: {operation_name}
Reason: {reason}

{suggested_alternative}
```

## Testing Checklist
- [ ] Detects 403 Forbidden responses
- [ ] Identifies InsufficientPrivileges error code
- [ ] Provides role-specific error messages
- [ ] Suggests appropriate actions for delegated vs service principal
- [ ] Shows workspace and user context in errors
- [ ] Offers alternative commands when available

## Related Skills
- `fabric-auth` - Authentication handling
- `error-handler` - Generic error handling
