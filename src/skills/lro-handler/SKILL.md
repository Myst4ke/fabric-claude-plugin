---
name: lro-handler
description: Handle Microsoft Fabric long-running operations (LRO) with intelligent polling and progress reporting
---

# Long-Running Operation (LRO) Handler Skill

## Purpose
Manage asynchronous operations in Microsoft Fabric that return 202 Accepted and require polling for completion status. This skill provides intelligent polling with exponential backoff, progress reporting, and timeout management.

## When to Use
- When API returns HTTP 202 Accepted
- Operations that typically take >5 seconds to complete
- Create, update, load, refresh, and other async operations

**Common LRO Operations:**
- Creating items (lakehouses, notebooks, semantic models)
- Loading data to lakehouse tables
- Refreshing datasets/dataflows
- Updating item definitions
- Running notebooks or pipelines
- Table maintenance operations (V-Order, Z-Order, VACUUM)

## Prerequisites
- Initial API response with 202 Accepted status
- Response headers containing operation tracking information
- Valid access token for polling requests

## Implementation Steps

### 1. Detect Long-Running Operation
Check if the initial API response indicates an async operation:

**HTTP Status**: 202 Accepted

**Required Response Headers:**
- `Location`: URL to poll for operation status or result
- `x-ms-operation-id`: Unique identifier for the operation
- `Retry-After`: Suggested seconds to wait before first poll (optional)

**Example Initial Response:**
```
HTTP/1.1 202 Accepted
Location: https://api.fabric.microsoft.com/v1/operations/abc-123-def
x-ms-operation-id: abc-123-def-456
Retry-After: 5
Content-Type: application/json

{
  "id": "abc-123-def-456",
  "status": "Running",
  "createdDateTime": "2024-01-15T10:30:00Z"
}
```

### 2. Extract Operation Details
Parse response headers and body:

```bash
# Extract from headers
LOCATION=$(echo "$headers" | grep -i "Location:" | cut -d' ' -f2)
OPERATION_ID=$(echo "$headers" | grep -i "x-ms-operation-id:" | cut -d' ' -f2)
RETRY_AFTER=$(echo "$headers" | grep -i "Retry-After:" | cut -d' ' -f2)

# Default Retry-After if not provided
RETRY_AFTER=${RETRY_AFTER:-5}
```

**Validation:**
- Location must be a valid HTTPS URL
- Operation ID must be a GUID format
- Retry-After should be a positive integer (seconds)

### 3. Initialize Polling Configuration

**Polling Strategy:**
```bash
# Configuration
INITIAL_DELAY=${RETRY_AFTER:-5}      # Use Retry-After or default 5s
POLL_INTERVAL=5                      # Base poll interval (seconds)
MAX_POLL_INTERVAL=60                 # Maximum poll interval (seconds)
MAX_ATTEMPTS=120                     # Maximum polling attempts (10 minutes with 5s interval)
BACKOFF_MULTIPLIER=1.5              # Exponential backoff multiplier

# State tracking
attempt=0
current_interval=$INITIAL_DELAY
start_time=$(date +%s)
```

### 4. Poll Operation Status
Make GET request to the Location URL or operation status endpoint:

**Polling Endpoint:**
```
GET {Location URL}
# or
GET https://api.fabric.microsoft.com/v1/operations/{operationId}
Authorization: Bearer {access_token}
```

**Expected Response Structure:**
```json
{
  "id": "abc-123-def-456",
  "status": "Running|Succeeded|Failed|Cancelled",
  "createdDateTime": "2024-01-15T10:30:00Z",
  "lastUpdatedDateTime": "2024-01-15T10:35:00Z",
  "percentComplete": 45,
  "error": {
    "code": "ErrorCode",
    "message": "Error details"
  }
}
```

**Status Values:**
- `Running` or `InProgress`: Operation still in progress
- `Succeeded`: Operation completed successfully
- `Failed`: Operation failed
- `Cancelled`: Operation was cancelled by user
- `NotStarted`: Operation queued but not yet started

### 5. Handle Different Operation States

#### State: Running/InProgress
```
⏳ Operation in progress... (attempt {attempt}/{max_attempts})
   Status: Running
   Progress: {percentComplete}%
   Elapsed time: {elapsed_seconds}s
   Next check in {current_interval}s
```

**Actions:**
1. Display progress update to user
2. Wait `current_interval` seconds
3. Increase interval with backoff: `new_interval = min(current_interval * 1.5, 60)`
4. Increment attempt counter
5. Continue to next poll

#### State: Succeeded
```
✅ Operation completed successfully
   Duration: {total_duration}s
   Operation ID: {operation_id}
```

**Actions:**
1. If Location URL changed (indicates result endpoint), fetch final result:
   ```
   GET {new_location}
   Authorization: Bearer {access_token}
   ```
2. Return success with operation details
3. Stop polling

#### State: Failed
```
❌ Operation failed

Error: {error.message}
Error Code: {error.code}
Operation ID: {operation_id}
Duration: {total_duration}s

Actions:
• Check error details above
• Verify input parameters
• Review operation logs
• Retry operation if error is transient
```

**Actions:**
1. Parse error details from response
2. Use error-handler skill to format error message
3. Return failure with error context
4. Stop polling

#### State: Cancelled
```
⚠️ Operation was cancelled

Operation ID: {operation_id}
Duration: {total_duration}s
```

**Actions:**
1. Return cancellation status
2. Stop polling

### 6. Implement Intelligent Polling

**Exponential Backoff Algorithm:**
```bash
poll_operation() {
  operation_id=$1
  location_url=$2

  attempt=0
  max_attempts=120
  poll_interval=5
  max_interval=60
  start_time=$(date +%s)

  while [ $attempt -lt $max_attempts ]; do
    attempt=$((attempt + 1))
    elapsed=$(($(date +%s) - start_time))

    # Make polling request
    response=$(curl -s -X GET "$location_url" \
      -H "Authorization: Bearer $ACCESS_TOKEN")

    status=$(echo "$response" | jq -r '.status')
    percent=$(echo "$response" | jq -r '.percentComplete // 0')

    case "$status" in
      "Succeeded")
        echo "✅ Operation completed successfully (${elapsed}s)"
        return 0
        ;;
      "Failed")
        error_msg=$(echo "$response" | jq -r '.error.message')
        echo "❌ Operation failed: $error_msg"
        return 1
        ;;
      "Cancelled")
        echo "⚠️ Operation was cancelled"
        return 2
        ;;
      "Running"|"InProgress"|"NotStarted")
        echo "⏳ Progress: ${percent}% | Elapsed: ${elapsed}s | Next check: ${poll_interval}s"
        sleep $poll_interval
        # Exponential backoff with cap
        poll_interval=$(awk "BEGIN {print int($poll_interval * 1.5)}")
        if [ $poll_interval -gt $max_interval ]; then
          poll_interval=$max_interval
        fi
        ;;
      *)
        echo "⚠️ Unknown status: $status"
        sleep $poll_interval
        ;;
    esac
  done

  echo "❌ Operation timeout (exceeded ${max_attempts} attempts)"
  return 3
}
```

**Polling Intervals:**
```
Attempt 1:   5s (initial)
Attempt 2:   7s (5 * 1.5)
Attempt 3:  10s (7 * 1.5)
Attempt 4:  15s (10 * 1.5)
Attempt 5:  22s (15 * 1.5)
Attempt 6:  33s (22 * 1.5)
Attempt 7:  49s (33 * 1.5)
Attempt 8:  60s (capped at max)
Attempt 9+: 60s (capped)
```

### 7. Handle Timeout Scenarios

**Timeout after Maximum Attempts:**
```
❌ Operation timeout

The operation is taking longer than expected.

Operation ID: {operation_id}
Duration: {elapsed_time}s
Last known status: {last_status}
Last known progress: {last_percent}%

Actions:
• Operation may still be running in the background
• Check operation status manually:
  /fabric:get-operation-status {operation_id}
• Check Fabric capacity performance
• Contact support if issue persists

Operation ID for reference: {operation_id}
```

### 8. Progress Reporting Strategies

#### Simple Progress Bar
```
⏳ Creating lakehouse...
   [████████████--------] 60% complete
   Elapsed: 45s | Estimated remaining: 30s
```

#### Detailed Progress Updates
```
⏳ Loading data to table (attempt 12/120)
   Status: Running
   Progress: 67%
   Rows processed: 1,340,000 / 2,000,000
   Elapsed: 60s
   Estimated remaining: 30s
   Next check in: 15s
```

#### Minimal Updates (for quick operations)
```
⏳ Creating notebook... (5s)
⏳ Creating notebook... (12s)
✅ Notebook created successfully (18s)
```

### 9. Handle Special Cases

#### Case 1: Immediate Completion
Some operations return 202 but complete immediately:
```
HTTP/1.1 202 Accepted
Location: https://api.fabric.microsoft.com/v1/operations/abc-123
x-ms-operation-id: abc-123

# First poll returns Succeeded immediately
# Display: ✅ Operation completed (1s)
```

#### Case 2: No percentComplete
Some operations don't report progress:
```json
{
  "status": "Running",
  "percentComplete": null
}
```
Display: `⏳ Operation in progress... (no progress data available)`

#### Case 3: Location URL Changes
Initial Location may redirect to result URL:
```
Initial: /operations/abc-123
Final:   /workspaces/{id}/items/{itemId}
```
Follow the redirect and fetch final resource.

#### Case 4: Network Errors During Polling
Apply retry logic from error-handler skill:
- Retry network errors 3 times
- Don't count network retries against max_attempts
- Display: `⚠️ Network error during polling, retrying...`

### 10. Cancellation Support

**User-Initiated Cancellation:**
Allow user to cancel long-running operations:
```bash
# Detect Ctrl+C
trap 'handle_cancellation' SIGINT

handle_cancellation() {
  echo ""
  echo "⚠️ Cancellation requested..."
  echo "Do you want to cancel the operation? (y/n)"
  read -r response

  if [ "$response" = "y" ]; then
    # Call cancellation endpoint
    curl -X POST "https://api.fabric.microsoft.com/v1/operations/${operation_id}/cancel" \
      -H "Authorization: Bearer $ACCESS_TOKEN"
    echo "✅ Cancellation request sent"
    exit 130
  else
    echo "Continuing operation..."
  fi
}
```

## Input Parameters
- `location_url`: String (URL from Location header)
- `operation_id`: String (GUID from x-ms-operation-id)
- `retry_after`: Integer (initial delay in seconds)
- `access_token`: String (for polling requests)
- `operation_context`: String (e.g., "Creating lakehouse", "Loading data")

## Output
- **Success**: Final operation result with duration
- **Failure**: Error message with operation context
- **Timeout**: Timeout message with operation ID for manual checking
- **Progress updates**: Periodic status messages to user

## Performance Optimization
1. **Adaptive polling**: Increase interval for long operations
2. **Efficient parsing**: Use jq for JSON parsing instead of complex scripts
3. **Connection reuse**: Keep HTTP connections alive during polling
4. **Parallel operations**: Don't block other commands during polling (use background jobs if needed)

## Example Usage

### Scenario 1: Quick Operation (Item Creation)
```bash
# User creates a notebook
/fabric:create-notebook my-workspace my-notebook

# API returns 202 Accepted
# LRO handler invoked

# Output to user:
⏳ Creating notebook... (5s)
⏳ Creating notebook... (10s)
✅ Notebook created successfully (12s)

Notebook ID: abc-123-def-456
Workspace: my-workspace
```

### Scenario 2: Slow Operation (Data Loading)
```bash
# User loads large dataset
/fabric:load-table my-workspace my-lakehouse sales_data /data/sales.parquet

# API returns 202 Accepted
# LRO handler invoked

# Output to user:
⏳ Loading data to table... (5s)
   Progress: 10%

⏳ Loading data to table... (12s)
   Progress: 35%

⏳ Loading data to table... (25s)
   Progress: 67%

⏳ Loading data to table... (42s)
   Progress: 92%

✅ Data loaded successfully (54s)

Rows loaded: 2,000,000
Table: sales_data
Lakehouse: my-lakehouse
```

### Scenario 3: Failed Operation
```bash
# User attempts operation that fails
/fabric:refresh-model my-workspace my-model

# API returns 202 Accepted
# LRO handler polls for status

# Output to user:
⏳ Refreshing semantic model... (5s)
   Progress: 20%

❌ Operation failed (18s)

Error: Data source authentication failed
Error Code: DataSourceAuthenticationError

Actions:
• Update data source credentials
• Verify data source connection
• Check firewall rules

Operation ID: abc-123-def-456
```

### Scenario 4: Operation Timeout
```bash
# User starts operation that hangs
/fabric:create-lakehouse my-workspace huge-lakehouse

# LRO handler polls for 10 minutes

# Output to user:
⏳ Creating lakehouse... (5s) [Progress: 0%]
⏳ Creating lakehouse... (12s) [Progress: 5%]
...
⏳ Creating lakehouse... (600s) [Progress: 67%]

❌ Operation timeout (exceeded 120 polling attempts)

The operation is taking longer than expected but may still complete.

Operation ID: abc-123-def-456
Last known progress: 67%

Actions:
• Check operation status: /fabric:get-operation-status abc-123-def-456
• Monitor capacity performance
• Contact support if needed
```

## Testing Checklist
- [ ] Quick operation (completes in 1 poll) → Success message
- [ ] Normal operation with progress → Progress updates displayed
- [ ] Slow operation with backoff → Poll intervals increase appropriately
- [ ] Failed operation → Error displayed with context
- [ ] Operation timeout → Timeout message with operation ID
- [ ] Network error during polling → Retry logic works
- [ ] User cancellation (Ctrl+C) → Graceful cancellation
- [ ] No percentComplete field → Handles gracefully
- [ ] Location URL changes → Follows redirect correctly

## Related Skills
- `error-handler` - Handles errors during polling
- `fabric-auth` - Provides access token for polling requests

## API Documentation
- **Fabric LRO Pattern**: https://learn.microsoft.com/en-us/rest/api/fabric/articles/long-running-operation
- **Operation Status API**: https://learn.microsoft.com/en-us/rest/api/fabric/core/operations
