---
description: List all accessible Microsoft Fabric workspaces
argument-hint: [--role <role>] [--format table|json]
---

# /fabric:list-workspaces

## Purpose
Retrieve and display all Microsoft Fabric workspaces accessible to the authenticated service principal. This command automatically handles pagination for large result sets and provides filtering options.

## Arguments
- `--role <role>`: Optional. Filter workspaces by your role (Admin, Member, Contributor, Viewer)
- `--format <format>`: Optional. Output format - `table` (default) or `json`

## Prerequisites
- Configured credentials (FABRIC_TENANT_ID, FABRIC_CLIENT_ID, FABRIC_CLIENT_SECRET)
- Service principal enabled in Fabric Admin Portal
- Service principal added to at least one workspace (or will show empty list)

## Instructions

### 1. Validate Inputs
Check optional arguments if provided:

```bash
role_filter=""
output_format="table"

# Parse arguments
while [ "$#" -gt 0 ]; do
  case "$1" in
    --role)
      role_filter="$2"
      # Validate role value
      if [[ ! "$role_filter" =~ ^(Admin|Member|Contributor|Viewer)$ ]]; then
        echo "❌ Invalid role: $role_filter"
        echo "Valid roles: Admin, Member, Contributor, Viewer"
        exit 1
      fi
      shift 2
      ;;
    --format)
      output_format="$2"
      if [[ ! "$output_format" =~ ^(table|json)$ ]]; then
        echo "❌ Invalid format: $output_format"
        echo "Valid formats: table, json"
        exit 1
      fi
      shift 2
      ;;
    *)
      echo "❌ Unknown argument: $1"
      echo "Usage: /fabric:list-workspaces [--role <role>] [--format table|json]"
      exit 1
      ;;
  esac
done
```

### 2. Authenticate
Use the fabric-auth skill to obtain an access token:

```bash
echo "🔐 Authenticating..."

# Use fabric-auth skill
ACCESS_TOKEN=$(fabric_auth_skill)

if [ $? -ne 0 ] || [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Authentication failed"
  echo ""
  echo "Please run /fabric:configure to set up credentials"
  exit 1
fi
```

### 3. Make Initial API Request
Fetch the first page of workspaces:

```bash
echo "📄 Fetching workspaces..."

# API endpoint
ENDPOINT="https://api.fabric.microsoft.com/v1/workspaces"

# Make request
response=$(curl -s -w "\n%{http_code}" -X GET "$ENDPOINT" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

# Check for errors
if [ "$http_code" != "200" ]; then
  echo "❌ API request failed (HTTP $http_code)"
  echo ""

  # Use error-handler skill to format error
  error_code=$(echo "$response_body" | jq -r '.error.code // "Unknown"')
  error_msg=$(echo "$response_body" | jq -r '.error.message // "No message"')

  echo "Error: $error_code"
  echo "Message: $error_msg"
  echo ""

  case "$http_code" in
    "401")
      echo "Authentication issue. Run /fabric:test-connection to diagnose."
      ;;
    "403")
      echo "Service principal may not be enabled in Fabric Admin Portal."
      echo "Or you don't have access to any workspaces yet."
      ;;
    "429")
      echo "Rate limited. Please wait a moment and try again."
      ;;
    *)
      echo "Check your connection and try again."
      ;;
  esac

  exit 1
fi
```

### 4. Handle Pagination
Use pagination-handler skill to fetch all pages:

```bash
# Extract first page results
all_workspaces=$(echo "$response_body" | jq -r '.value')
page_count=1
total_count=$(echo "$all_workspaces" | jq 'length')

# Check for continuation token
continuation_token=$(echo "$response_body" | jq -r '.continuationToken // empty')

# Fetch remaining pages if pagination exists
while [ -n "$continuation_token" ] && [ "$continuation_token" != "null" ]; do
  page_count=$((page_count + 1))
  echo "📄 Fetching page $page_count..."

  # Fetch next page
  response=$(curl -s -w "\n%{http_code}" -X GET \
    "${ENDPOINT}?continuationToken=${continuation_token}" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json")

  http_code=$(echo "$response" | tail -n1)
  response_body=$(echo "$response" | head -n-1)

  if [ "$http_code" != "200" ]; then
    echo "⚠️ Error fetching page $page_count, stopping pagination"
    break
  fi

  # Append page results
  page_results=$(echo "$response_body" | jq -r '.value')
  all_workspaces=$(echo "$all_workspaces $page_results" | jq -s 'add')
  page_size=$(echo "$page_results" | jq 'length')
  total_count=$((total_count + page_size))

  # Get next continuation token
  continuation_token=$(echo "$response_body" | jq -r '.continuationToken // empty')

  # Small delay to respect rate limits
  sleep 0.3
done

if [ $page_count -gt 1 ]; then
  echo "✅ Fetched $total_count workspaces ($page_count pages)"
else
  echo "✅ Found $total_count workspace(s)"
fi
```

### 5. Apply Filters
Filter results by role if specified:

```bash
if [ -n "$role_filter" ]; then
  echo "🔍 Filtering by role: $role_filter..."

  # Note: API doesn't provide role information directly in list endpoint
  # This would require additional API calls per workspace to get role info
  # For now, show all and note the limitation

  echo ""
  echo "ℹ️  Note: Role filtering requires additional API calls per workspace."
  echo "    Displaying all workspaces. Use /fabric:get-workspace to see your role."
  echo ""
fi
```

### 6. Format and Display Results

#### Table Format (Default)
```bash
if [ "$output_format" = "table" ]; then
  if [ "$total_count" -eq 0 ]; then
    echo ""
    echo "ℹ️  No workspaces found"
    echo ""
    echo "Possible reasons:"
    echo "  • Service principal not added to any workspaces"
    echo "  • No workspaces created yet"
    echo "  • Insufficient permissions"
    echo ""
    echo "To create a workspace or get access:"
    echo "  1. Go to Fabric portal (app.fabric.microsoft.com)"
    echo "  2. Create a workspace or ask admin for access"
    echo "  3. Add your service principal with appropriate role"
    exit 0
  fi

  echo ""
  echo "Microsoft Fabric Workspaces ($total_count total)"
  echo "════════════════════════════════════════════════════════════════════════"
  echo ""

  # Format as table
  echo "$all_workspaces" | jq -r '
    ["NAME", "ID", "TYPE", "CAPACITY"],
    ["─────", "────", "──────", "────────"],
    (.[] |
      [
        .displayName,
        .id,
        .type // "Workspace",
        .capacityId // "Not assigned"
      ]
    )
    | @tsv
  ' | column -t -s $'\t'

  echo ""
  echo "════════════════════════════════════════════════════════════════════════"
  echo ""
  echo "💡 Tips:"
  echo "  • Use /fabric:get-workspace <workspace-id> for detailed information"
  echo "  • Create items: /fabric:create-lakehouse <workspace-id> <name>"
  echo ""
fi
```

#### JSON Format
```bash
if [ "$output_format" = "json" ]; then
  # Output raw JSON
  echo "$all_workspaces" | jq '.'
fi
```

### 7. Provide Next Steps
Suggest relevant follow-up commands:

```bash
if [ "$total_count" -gt 0 ] && [ "$output_format" = "table" ]; then
  echo "Next steps:"
  echo "  • Get workspace details: /fabric:get-workspace <workspace-id>"
  echo "  • List items in workspace: /fabric:list-items <workspace-id>"
  echo "  • Create lakehouse: /fabric:create-lakehouse <workspace-id> <name>"
  echo ""
fi
```

## Example Output

### Table Format with Multiple Workspaces
```
/fabric:list-workspaces

🔐 Authenticating...
📄 Fetching workspaces...
📄 Fetching page 2...
✅ Fetched 247 workspaces (2 pages)

Microsoft Fabric Workspaces (247 total)
════════════════════════════════════════════════════════════════════════

NAME                          ID                                    TYPE        CAPACITY
─────                         ────                                  ──────      ────────
Dev Workspace                 abc-123-def-456-ghi-789-jkl-012       Workspace   cap-prod-001
Test Workspace                def-456-ghi-789-jkl-012-mno-345       Workspace   cap-test-001
Production Workspace          ghi-789-jkl-012-mno-345-pqr-678       Workspace   cap-prod-001
Analytics Workspace           jkl-012-mno-345-pqr-678-stu-901       Workspace   cap-prod-002
Marketing Dashboard Workspace mno-345-pqr-678-stu-901-vwx-234       Workspace   Not assigned
Finance Reporting Workspace   pqr-678-stu-901-vwx-234-yz0-567       Workspace   cap-prod-001
... [241 more workspaces]

════════════════════════════════════════════════════════════════════════

💡 Tips:
  • Use /fabric:get-workspace <workspace-id> for detailed information
  • Create items: /fabric:create-lakehouse <workspace-id> <name>

Next steps:
  • Get workspace details: /fabric:get-workspace <workspace-id>
  • List items in workspace: /fabric:list-items <workspace-id>
  • Create lakehouse: /fabric:create-lakehouse <workspace-id> <name>
```

### JSON Format
```
/fabric:list-workspaces --format json

🔐 Authenticating...
📄 Fetching workspaces...
✅ Found 12 workspace(s)

[
  {
    "id": "abc-123-def-456-ghi-789-jkl-012",
    "displayName": "Dev Workspace",
    "description": "Development environment",
    "type": "Workspace",
    "capacityId": "cap-prod-001",
    "capacityAssignmentProgress": null
  },
  {
    "id": "def-456-ghi-789-jkl-012-mno-345",
    "displayName": "Test Workspace",
    "description": "",
    "type": "Workspace",
    "capacityId": "cap-test-001",
    "capacityAssignmentProgress": null
  },
  ...
]
```

### Empty Result
```
/fabric:list-workspaces

🔐 Authenticating...
📄 Fetching workspaces...
✅ Found 0 workspace(s)

ℹ️  No workspaces found

Possible reasons:
  • Service principal not added to any workspaces
  • No workspaces created yet
  • Insufficient permissions

To create a workspace or get access:
  1. Go to Fabric portal (app.fabric.microsoft.com)
  2. Create a workspace or ask admin for access
  3. Add your service principal with appropriate role
```

## Error Scenarios

### Scenario 1: Authentication Failure
```
/fabric:list-workspaces

🔐 Authenticating...
❌ Authentication failed

Please run /fabric:configure to set up credentials
```

### Scenario 2: Service Principal Not Enabled
```
/fabric:list-workspaces

🔐 Authenticating...
📄 Fetching workspaces...
❌ API request failed (HTTP 403)

Error: Forbidden
Message: Service principal access is not enabled

Service principal may not be enabled in Fabric Admin Portal.
Or you don't have access to any workspaces yet.
```

### Scenario 3: Rate Limiting
```
/fabric:list-workspaces

🔐 Authenticating...
📄 Fetching workspaces...
❌ API request failed (HTTP 429)

Error: TooManyRequests
Message: Request rate exceeded

Rate limited. Please wait a moment and try again.
```

### Scenario 4: Invalid Role Filter
```
/fabric:list-workspaces --role InvalidRole

❌ Invalid role: InvalidRole
Valid roles: Admin, Member, Contributor, Viewer
```

## Performance Considerations
- Typical response time: 200-500ms for first page
- Large result sets (>1000 workspaces): May take 5-10 seconds
- Pagination adds ~200ms per additional page
- Token acquisition (first call): +300-500ms

## Related Commands
- `/fabric:get-workspace <workspace-id>` - Get detailed workspace information
- `/fabric:create-workspace <name> <capacity-id>` - Create new workspace
- `/fabric:test-connection` - Verify API connectivity

## API Reference
- **Endpoint**: `GET https://api.fabric.microsoft.com/v1/workspaces`
- **Authentication**: Bearer token
- **Response**: Paginated array of workspace objects
- **Pagination**: continuationToken pattern
- **Rate Limit**: Standard Fabric API limits apply

## Testing Checklist
- [ ] Valid credentials → Workspaces listed successfully
- [ ] Multiple pages → All pages fetched automatically
- [ ] Empty result → Clear message with next steps
- [ ] --format json → Valid JSON output
- [ ] --role filter → Validation works (note: filtering not fully implemented)
- [ ] Authentication error → Clear error with instructions
- [ ] 403 error → Service principal guidance
- [ ] 429 error → Rate limit message
- [ ] Network timeout → Error handled gracefully
