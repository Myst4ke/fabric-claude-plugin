---
description: Get notebook definition (cells and code)
argument-hint: <workspace-id> <notebook-id> [--output <file>]
---

# /fabric:get-notebook-definition

## Purpose
Retrieve the complete notebook definition including all cells, code, outputs, and metadata in.ipynb format.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `notebook-id`: Required. GUID of the notebook
- `--output <file>`: Optional. Save to file instead of displaying

## Instructions

```bash
workspace_id="$1"
notebook_id="$2"
output_file=""

shift 2
while [[ $# -gt 0 ]]; do
  case $1 in
    --output) output_file="$2"; shift 2 ;;
    *) echo "❌ Unknown argument: $1"; exit 1 ;;
  esac
done

if [ -z "$workspace_id" ] || [ -z "$notebook_id" ]; then
  echo "❌ Workspace ID and notebook ID are required"
  exit 1
fi

if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid workspace ID"; exit 1
fi

if ! [[ "$notebook_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid notebook ID"; exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📥 Requesting definition..."

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/notebooks/$notebook_id/getDefinition" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)

if [ "$http_code" != "202" ]; then
  echo "❌ Failed (HTTP $http_code)"
  exit 1
fi

operation_id=$(echo "$response" | grep -i "^x-ms-operation-id:" | cut -d' ' -f2 | tr -d '\r')
echo "⏳ Retrieving definition..."

max_attempts=60
for ((i=0; i<$max_attempts; i++)); do
  sleep 3

  status_response=$(curl -s -X GET \
    "https://api.fabric.microsoft.com/v1/operations/$operation_id" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  status=$(echo "$status_response" | jq -r '.status')

  if [ "$status" = "Succeeded" ]; then
    location=$(echo "$status_response" | jq -r '.resourceLocation // empty')

    def_response=$(curl -s -X GET "$location" -H "Authorization: Bearer $ACCESS_TOKEN")
    definition=$(echo "$def_response" | jq '.definition.parts[0].payload')

    if [ -n "$output_file" ]; then
      echo "$definition" | base64 -d > "$output_file"
      echo "✅ Definition saved to: $output_file"
    else
      echo "✅ Definition retrieved:"
      echo "$definition" | base64 -d | jq '.'
    fi

    exit 0
  elif [ "$status" = "Failed" ]; then
    echo "❌ Operation failed"
    exit 1
  fi
done

echo "❌ Timeout"
exit 1
```

## Related Commands
- `/fabric:update-notebook-definition` - Update notebook code
- `/fabric:export-notebook` - Export with metadata
- `/fabric:import-notebook` - Import notebook

## API Reference
- **Endpoint**: `POST .../notebooks/{id}/getDefinition` (LRO)
- **Response**: 202 Accepted
- **Permissions**: Any workspace role
