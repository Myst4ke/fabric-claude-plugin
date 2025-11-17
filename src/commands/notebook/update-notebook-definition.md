---
description: Update notebook definition from file
argument-hint: <workspace-id> <notebook-id> <definition-file>
---

# /fabric:update-notebook-definition

## Purpose
Update notebook cells and code from a .ipynb file or definition JSON.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `notebook-id`: Required. GUID of the notebook
- `definition-file`: Required. Path to .ipynb file

## Instructions

```bash
workspace_id="$1"
notebook_id="$2"
definition_file="$3"

if [ -z "$workspace_id" ] || [ -z "$notebook_id" ] || [ -z "$definition_file" ]; then
  echo "❌ All arguments required"
  exit 1
fi

if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid workspace ID"; exit 1
fi

if ! [[ "$notebook_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid notebook ID"; exit 1
fi

if [ ! -f "$definition_file" ]; then
  echo "❌ File not found: $definition_file"
  exit 1
fi

if ! jq empty "$definition_file" 2>/dev/null; then
  echo "❌ Invalid JSON"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📤 Uploading definition..."

definition_content=$(cat "$definition_file" | jq -c '.')
encoded=$(echo "$definition_content" | base64)

request_body=$(jq -n \
  --arg payload "$encoded" \
  '{
    definition: {
      parts: [{
        path: "notebook-content.py",
        payload: $payload,
        payloadType: "InlineBase64"
      }]
    }
  }')

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/notebooks/$notebook_id/updateDefinition" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$request_body")

http_code=$(echo "$response" | tail -n1)

if [ "$http_code" != "202" ]; then
  echo "❌ Failed (HTTP $http_code)"
  exit 1
fi

operation_id=$(echo "$response" | grep -i "^x-ms-operation-id:" | cut -d' ' -f2 | tr -d '\r')
echo "⏳ Applying changes..."

max_attempts=60
for ((i=0; i<$max_attempts; i++)); do
  sleep 3

  status_response=$(curl -s -X GET \
    "https://api.fabric.microsoft.com/v1/operations/$operation_id" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  status=$(echo "$status_response" | jq -r '.status')
  percent=$(echo "$status_response" | jq -r '.percentComplete // 0')

  echo "   Progress: $percent%"

  if [ "$status" = "Succeeded" ]; then
    echo "✅ Definition updated successfully"
    echo ""
    echo "💡 Next steps:"
    echo "  • Execute: /fabric:run-notebook $workspace_id $notebook_id"
    echo "  • View: /fabric:get-notebook $workspace_id $notebook_id"
    exit 0
  elif [ "$status" = "Failed" ]; then
    error=$(echo "$status_response" | jq -r '.error.message // "Unknown"')
    echo "❌ Failed: $error"
    exit 1
  fi
done

echo "❌ Timeout"
exit 1
```

## API Reference
- **Endpoint**: `POST .../notebooks/{id}/updateDefinition` (LRO)
- **Response**: 202 Accepted
- **Permissions**: Contributor, Member, or Admin
