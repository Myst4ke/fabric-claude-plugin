---
description: Import notebook from .ipynb file
argument-hint: <workspace-id> <import-file> [--name <name>]
---

# /fabric:import-notebook

## Purpose
Import a notebook from .ipynb file, creating a new notebook in the workspace.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `import-file`: Required. Path to .ipynb file
- `--name <name>`: Optional. Override notebook name

## Instructions

```bash
workspace_id="$1"
import_file="$2"
override_name=""

shift 2
while [[ $# -gt 0 ]]; do
  case $1 in
    --name) override_name="$2"; shift 2 ;;
    *) echo "❌ Unknown argument: $1"; exit 1 ;;
  esac
done

if [ -z "$workspace_id" ] || [ -z "$import_file" ]; then
  echo "❌ Workspace ID and import file required"; exit 1
fi

if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid workspace ID"; exit 1
fi

if [ ! -f "$import_file" ]; then
  echo "❌ File not found: $import_file"; exit 1
fi

if ! jq empty "$import_file" 2>/dev/null; then
  echo "❌ Invalid JSON format"; exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

# Determine notebook name
if [ -n "$override_name" ]; then
  notebook_name="$override_name"
else
  notebook_name=$(jq -r '.metadata.name // "Imported Notebook"' "$import_file")
fi

echo "📤 Creating notebook: $notebook_name"

# Create notebook
create_body=$(jq -n --arg name "$notebook_name" '{displayName: $name, type: "Notebook"}')

create_response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$create_body")

create_http_code=$(echo "$create_response" | tail -n1)
create_body_response=$(echo "$create_response" | head -n-1)

if [ "$create_http_code" != "201" ] && [ "$create_http_code" != "202" ]; then
  echo "❌ Failed to create notebook"; exit 1
fi

notebook_id=$(echo "$create_body_response" | jq -r '.id')

if [ "$create_http_code" = "202" ]; then
  echo "⏳ Waiting for notebook creation..."
  operation_id=$(echo "$create_response" | grep -i "^x-ms-operation-id:" | cut -d' ' -f2 | tr -d '\r')

  for ((i=0; i<30; i++)); do
    sleep 2
    op_response=$(curl -s -X GET "https://api.fabric.microsoft.com/v1/operations/$operation_id" \
      -H "Authorization: Bearer $ACCESS_TOKEN")
    op_status=$(echo "$op_response" | jq -r '.status')

    if [ "$op_status" = "Succeeded" ]; then
      notebook_id=$(echo "$op_response" | jq -r '.resourceId')
      break
    elif [ "$op_status" = "Failed" ]; then
      echo "❌ Creation failed"; exit 1
    fi
  done
fi

echo "✅ Notebook created: $notebook_id"
echo "📝 Uploading definition..."

# Upload definition
definition_content=$(cat "$import_file" | jq -c '.')
encoded=$(echo "$definition_content" | base64)

update_body=$(jq -n --arg payload "$encoded" \
  '{definition: {parts: [{path: "notebook-content.py", payload: $payload, payloadType: "InlineBase64"}]}}')

update_response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/notebooks/$notebook_id/updateDefinition" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$update_body")

update_http_code=$(echo "$update_response" | tail -n1)

if [ "$update_http_code" != "202" ]; then
  echo "❌ Failed to upload definition"; exit 1
fi

update_op_id=$(echo "$update_response" | grep -i "^x-ms-operation-id:" | cut -d' ' -f2 | tr -d '\r')

for ((i=0; i<60; i++)); do
  sleep 3
  status_response=$(curl -s -X GET "https://api.fabric.microsoft.com/v1/operations/$update_op_id" \
    -H "Authorization: Bearer $ACCESS_TOKEN")
  status=$(echo "$status_response" | jq -r '.status')

  if [ "$status" = "Succeeded" ]; then
    echo "✅ Notebook imported successfully"
    echo ""
    echo "Name:        $notebook_name"
    echo "Notebook ID: $notebook_id"
    echo ""
    echo "💡 Next steps:"
    echo "  • View: /fabric:get-notebook $workspace_id $notebook_id"
    echo "  • Execute: /fabric:run-notebook $workspace_id $notebook_id"
    exit 0
  elif [ "$status" = "Failed" ]; then
    echo "❌ Import failed"; exit 1
  fi
done

echo "❌ Timeout"; exit 1
```

## API Reference
- **Create**: `POST .../items` (LRO)
- **Update Definition**: `POST .../notebooks/{id}/updateDefinition` (LRO)
- **Permissions**: Contributor, Member, or Admin
