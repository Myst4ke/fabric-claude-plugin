---
description: Get lakehouse details
argument-hint: <workspace-id> <lakehouse-id>
---

# /fabric:get-lakehouse

## Purpose
Retrieve detailed information about a specific lakehouse.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `lakehouse-id`: Required. GUID of the lakehouse

## Instructions

```bash
workspace_id="$1"
lakehouse_id="$2"

if [ -z "$workspace_id" ] || [ -z "$lakehouse_id" ]; then
  echo "❌ Both IDs required"; exit 1
fi

if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid workspace ID"; exit 1
fi

if ! [[ "$lakehouse_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid lakehouse ID"; exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "🏞️  Fetching lakehouse details..."

response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/lakehouses/$lakehouse_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" != "200" ]; then
  echo "❌ Failed (HTTP $http_code)"; exit 1
fi

name=$(echo "$response_body" | jq -r '.displayName')
desc=$(echo "$response_body" | jq -r '.description // "No description"')
created=$(echo "$response_body" | jq -r '.createdDate // "N/A"')
modified=$(echo "$response_body" | jq -r '.lastModifiedDate // "N/A"')

echo "✅ Lakehouse retrieved"
echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║              LAKEHOUSE DETAILS                            ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "Name:          $name"
echo "ID:            $lakehouse_id"
echo "Description:   $desc"
echo ""
echo "Created:       $created"
echo "Last Modified: $modified"
echo ""
echo "Workspace ID:  $workspace_id"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "💡 Available operations:"
echo "  • List tables: /fabric:list-lakehouse-tables $workspace_id $lakehouse_id"
echo "  • List files: /fabric:list-lakehouse-files $workspace_id $lakehouse_id"
echo "  • Query data: /fabric:query-lakehouse $workspace_id $lakehouse_id"
echo "  • Load data: /fabric:load-table $workspace_id $lakehouse_id <table-name>"
```

## API Reference
- **Endpoint**: `GET .../lakehouses/{id}`
- **Response**: 200 OK
- **Permissions**: Any workspace role
