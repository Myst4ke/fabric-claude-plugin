---
name: error-handler
description: Handle Microsoft Fabric API errors with retry logic and user-friendly messages
---

# Error Handler Skill

## Purpose
Translate Microsoft Fabric API errors into user-friendly, actionable messages and implement intelligent retry logic for transient failures. This skill ensures consistent error handling across all plugin commands and agents.

## When to Use
- After every Fabric API request
- When HTTP status code is 4xx or 5xx
- When network errors occur
- When parsing API responses fails

## Prerequisites
- API response with HTTP status code and body
- Original request context (endpoint, method, parameters)

## Implementation Steps

### 1. Check HTTP Status Code
Examine the HTTP status code from the API response:
- **2xx (200-299)**: Success → No error handling needed
- **4xx (400-499)**: Client errors → Parse error details and provide guidance
- **5xx (500-599)**: Server errors → Implement retry logic
- **Network errors**: Connection timeout, DNS failures → Implement retry logic

### 2. Parse Error Response Body
Most Fabric API errors return JSON with error details:

```json
{
  "error": {
    "code": "ErrorCode",
    "message": "Detailed error message",
    "target": "specific_parameter",
    "details": [
      {
        "code": "NestedErrorCode",
        "message": "Additional context"
      }
    ]
  }
}
```

Extract:
- **error.code**: Machine-readable error identifier
- **error.message**: Human-readable error description
- **error.target**: Which parameter caused the error
- **error.details**: Additional error information

### 3. Map Errors to User-Friendly Messages
Translate common error codes into actionable guidance:

#### Authentication Errors (401 Unauthorized)

**Error Pattern:**
```
HTTP 401 Unauthorized
{
  "error": {
    "code": "Unauthorized",
    "message": "Authentication failed"
  }
}
```

**User Message:**
```
❌ Authentication failed

Possible causes:
1. Access token is expired or invalid
2. Token is missing from Authorization header
3. Service principal credentials are incorrect

Actions:
• Run `/fabric:configure` to update credentials
• Verify FABRIC_TENANT_ID, FABRIC_CLIENT_ID, FABRIC_CLIENT_SECRET are set
• Check token expiration (tokens expire after 60 minutes)

Technical details: {error.message}
```

#### Authorization Errors (403 Forbidden)

**Fabric-Specific Error Codes:**
- `InsufficientPrivileges`
- `PrincipalTypeNotSupported`
- `WorkspaceAccessDenied`
- `CapacityAccessDenied`

**User Message for InsufficientPrivileges:**
```
❌ Insufficient permissions

You don't have permission to perform this action.

Required permission: {required_permission}
Your current role: {current_role}

Actions:
• Contact workspace admin to grant appropriate permissions
• Required roles: Admin, Member, or Contributor
• For capacity operations: Capacity contributor role required

Technical details: {error.message}
```

**User Message for PrincipalTypeNotSupported:**
```
❌ Service principal not supported for this operation

This operation requires delegated user authentication (not service principal).

Affected operations:
• Creating certain item types
• Some admin operations
• User-specific actions

Actions:
• Use delegated auth flow (interactive login)
• Switch to user account authentication
• Check API documentation for operation requirements

Technical details: {error.message}
```

#### Not Found Errors (404 Not Found)

**Fabric-Specific Error Codes:**
- `WorkspaceNotFound`
- `ItemNotFound`
- `CapacityNotFound`
- `FolderNotFound`

**User Message:**
```
❌ Resource not found

The requested {resource_type} doesn't exist or you don't have access.

Resource ID: {resource_id}
Endpoint: {api_endpoint}

Actions:
• Verify the ID is correct (must be GUID format)
• Run `/fabric:list-workspaces` to see available workspaces
• Check if resource was deleted
• Verify you have read permissions

Technical details: {error.message}
```

#### Rate Limiting (429 Too Many Requests)

**Error Pattern:**
```
HTTP 429 Too Many Requests
Retry-After: 30
{
  "error": {
    "code": "TooManyRequests",
    "message": "Rate limit exceeded"
  }
}
```

**Retry Logic:**
1. Extract `Retry-After` header (seconds to wait)
2. If header missing, use exponential backoff: 1s, 2s, 4s, 8s, 16s
3. Display progress to user:
```
⏳ Rate limit exceeded. Waiting {retry_after} seconds before retry...
   Attempt {current_attempt} of {max_attempts}
```
4. Wait specified duration
5. Retry original request
6. Maximum 5 retry attempts for rate limiting

**User Message (after max retries):**
```
❌ Rate limit exceeded (maximum retries reached)

The Fabric API is currently rate limiting your requests.

Actions:
• Wait a few minutes before retrying
• Reduce frequency of API calls
• Consider batching operations
• Check if other processes are making concurrent requests

Retry-After: {retry_after} seconds
Technical details: {error.message}
```

#### Bad Request (400 Bad Request)

**Fabric-Specific Error Codes:**
- `InvalidRequest`
- `InvalidItemType`
- `InvalidParameter`
- `MissingParameter`

**User Message:**
```
❌ Invalid request

The request parameters are incorrect or missing.

Error: {error.message}
Parameter: {error.target}

Actions:
• Check command syntax: /fabric:command-name --help
• Verify parameter formats (GUIDs, names, values)
• Ensure required parameters are provided
• Check parameter value constraints

Examples:
  Workspace ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx (GUID format)
  Item Name: 1-256 characters, alphanumeric
  Item Type: Lakehouse, Notebook, DataPipeline, etc.

Technical details: {error.message}
```

#### Server Errors (500-599)

**Error Codes:**
- `InternalServerError` (500)
- `ServiceUnavailable` (503)
- `GatewayTimeout` (504)

**Retry Logic:**
1. Server errors are often transient
2. Implement exponential backoff: 1s, 2s, 4s, 8s, 16s
3. Maximum 3 retry attempts
4. Display progress:
```
⚠️ Server error (attempt {current_attempt} of {max_attempts})
   Retrying in {wait_time} seconds...
```

**User Message (after retries):**
```
❌ Microsoft Fabric service error

The Fabric API encountered an internal error.

HTTP Status: {status_code}
Error: {error.message}

Actions:
• Wait a few minutes and try again
• Check Fabric service status: https://status.fabric.microsoft.com
• If issue persists, contact Microsoft support
• Check Azure service health dashboard

Technical details: {error.code} - {error.message}
```

#### Network Errors

**Error Types:**
- Connection timeout
- DNS resolution failure
- SSL/TLS errors
- Connection refused

**Retry Logic:**
1. Implement exponential backoff: 1s, 2s, 4s
2. Maximum 3 retry attempts
3. Different handling for different error types

**User Message:**
```
❌ Network error

Failed to connect to Microsoft Fabric API.

Error: {network_error_type}
Endpoint: {api_endpoint}

Actions:
• Check internet connectivity
• Verify firewall/proxy settings
• Check DNS resolution: nslookup api.fabric.microsoft.com
• Verify corporate network policies
• Try again in a few minutes

Technical details: {error_details}
```

#### Conflict Errors (409 Conflict)

**Fabric-Specific Error Codes:**
- `NameConflict`
- `ResourceAlreadyExists`
- `ConcurrentOperationInProgress`

**User Message:**
```
❌ Resource conflict

A resource with this name already exists, or a conflicting operation is in progress.

Conflict: {error.message}
Resource: {resource_name}

Actions:
• Choose a different name
• Delete existing resource first (if intentional)
• Wait for ongoing operation to complete
• Check for duplicate resources: /fabric:list-items {workspace_id}

Technical details: {error.message}
```

### 4. Implement Retry Logic

**Retry Decision Matrix:**

| HTTP Status | Error Type | Retry? | Max Attempts | Backoff Strategy |
|-------------|------------|--------|--------------|------------------|
| 429 | Rate Limit | Yes | 5 | Use Retry-After header |
| 500 | Server Error | Yes | 3 | Exponential (1s, 2s, 4s, 8s) |
| 502 | Bad Gateway | Yes | 3 | Exponential |
| 503 | Service Unavailable | Yes | 3 | Exponential |
| 504 | Gateway Timeout | Yes | 3 | Exponential |
| 401 | Unauthorized | No | 0 | Token might be expired, re-auth once |
| 403 | Forbidden | No | 0 | Permission issue, won't resolve with retry |
| 404 | Not Found | No | 0 | Resource doesn't exist |
| 400 | Bad Request | No | 0 | Client error, fix parameters |
| 409 | Conflict | No | 0 | Resource conflict, user action needed |
| Network Timeout | Timeout | Yes | 3 | Exponential (2s, 4s, 8s) |
| DNS Failure | Network | Yes | 2 | Linear (5s, 10s) |

**Exponential Backoff Formula:**
```
wait_time = base_delay * (2 ^ (attempt - 1))
base_delay = 1 second
max_wait = 16 seconds

Attempt 1: 1s
Attempt 2: 2s
Attempt 3: 4s
Attempt 4: 8s
Attempt 5: 16s
```

**Backoff Implementation:**
```bash
retry_count=0
max_retries=3
base_delay=1

while [ $retry_count -lt $max_retries ]; do
  # Make API request
  response=$(curl ...)
  status_code=$(echo "$response" | jq -r '.status_code')

  if should_retry "$status_code"; then
    retry_count=$((retry_count + 1))
    wait_time=$((base_delay * (2 ** (retry_count - 1))))
    echo "⏳ Retrying in ${wait_time}s (attempt $retry_count of $max_retries)..."
    sleep $wait_time
  else
    break
  fi
done
```

### 5. Log Errors for Debugging

**Error Log Format:**
```
[{timestamp}] ERROR: {error_code}
Command: {command_name}
Endpoint: {api_endpoint}
Method: {http_method}
Status: {status_code}
Message: {error.message}
Request ID: {x-ms-request-id header}
Correlation ID: {x-ms-correlation-id header}
User: {fabric_user_principal}
```

**Log Location:**
- `~/.claude/logs/fabric-plugin-errors.log` (append mode)
- Rotate logs when > 10MB
- Keep last 5 log files

## Input Parameters
- `http_status_code`: Integer (200-599 or network error code)
- `response_body`: JSON string from API
- `request_context`: Object with endpoint, method, parameters
- `attempt_number`: Integer (for retry tracking)

## Output
- **User-friendly error message**: String to display to user
- **Retry decision**: Boolean (should retry?)
- **Wait time**: Integer (seconds to wait before retry)
- **Error details**: Object for logging

## Error Handling Priority
1. **User experience first**: Clear, actionable messages
2. **Avoid jargon**: Explain technical terms
3. **Provide solutions**: Always suggest next steps
4. **Include context**: Show relevant IDs, parameters
5. **Enable self-service**: Link to commands/docs
6. **Respect rate limits**: Don't hammer the API
7. **Log for debugging**: Capture details for support

## Example Usage

### Scenario 1: Rate Limit with Retry
```bash
# User command triggers API call
/fabric:list-workspaces

# API returns 429 with Retry-After: 30
# error-handler skill invoked

# Output to user:
⏳ Rate limit exceeded. Waiting 30 seconds before retry...
   Attempt 1 of 5

# After 30 seconds, retry automatically
✅ Workspaces retrieved successfully
```

### Scenario 2: Permission Error (No Retry)
```bash
/fabric:delete-workspace abc-123

# API returns 403 Forbidden
# error-handler skill invoked

# Output to user:
❌ Insufficient permissions

You don't have permission to delete this workspace.

Required role: Admin
Your current role: Viewer

Actions:
• Contact workspace admin to grant Admin role
• Run `/fabric:list-workspaces` to see your permissions

Technical details: Principal does not have required permissions
```

### Scenario 3: Server Error with Retries
```bash
/fabric:create-lakehouse my-workspace my-lakehouse

# API returns 500 Internal Server Error
# error-handler skill invoked

# Output to user:
⚠️ Server error (attempt 1 of 3)
   Retrying in 1 seconds...

# Retry 1 fails (500)
⚠️ Server error (attempt 2 of 3)
   Retrying in 2 seconds...

# Retry 2 succeeds
✅ Lakehouse created successfully
```

## Testing Checklist
- [ ] 401 error → Clear auth failure message, no retry
- [ ] 403 error → Permission guidance, no retry
- [ ] 404 error → Resource not found message, no retry
- [ ] 429 error → Retry with Retry-After header (5 attempts)
- [ ] 500 error → Retry with exponential backoff (3 attempts)
- [ ] 503 error → Retry with backoff
- [ ] Network timeout → Retry 3 times
- [ ] All retries exhausted → Final error message with context
- [ ] Error logging → Errors written to log file with context

## Related Skills
- `fabric-auth` - May trigger re-authentication on 401 errors
- `lro-handler` - Coordinates with error handling for async operations

## API Documentation
- **Fabric API Error Codes**: https://learn.microsoft.com/en-us/rest/api/fabric/articles/error-codes
- **HTTP Status Codes**: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
