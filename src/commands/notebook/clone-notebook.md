---
description: Clone a notebook
argument-hint: <workspace-id> <notebook-id> <new-name> [--target-workspace <id>]
---

# /fabric:clone-notebook

## Purpose
Create a duplicate of a notebook, optionally in a different workspace.

## Arguments
- `workspace-id`: Required. Source workspace GUID
- `notebook-id`: Required. Notebook GUID to clone
- `new-name`: Required. Name for cloned notebook
- `--target-workspace <id>`: Optional. Target workspace (default: same)

## Instructions

```bash
workspace_id="$1"
notebook_id="$2"
new_name="$3"
target_workspace=""

shift 3
while [[ $# -gt 0 ]]; do
  case $1 in
    --target-workspace) target_workspace="$2"; shift 2 ;;
    *) echo "❌ Unknown argument: $1"; exit 1 ;;
  esac
done

if [ -z "$workspace_id" ] || [ -z "$notebook_id" ] || [ -z "$new_name" ]; then
  echo "❌ All arguments required"; exit 1
fi

[ -z "$target_workspace" ] && target_workspace="$workspace_id"

if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid workspace ID"; exit 1
fi

if ! [[ "$notebook_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid notebook ID"; exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📥 Getting source definition..."

# Get definition (simplified - reuse export logic)
get_response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/notebooks/$notebook_id/getDefinition" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if [ "$(echo "$get_response" | tail -n1)" != "202" ]; then
  echo "❌ Failed to get definition"; exit 1
fi

operation_id=$(echo "$get_response" | grep -i "^x-ms-operation-id:" | cut -d' ' -f2 | tr -d '\r')

for ((i=0; i<60; i++)); do
  sleep 2
  status_response=$(curl -s -X GET "https://api.fabric.microsoft.com/v1/operations/$operation_id" \
    -H "Authorization: Bearer $ACCESS_TOKEN")
  status=$(echo "$status_response" | jq -r '.status')

  if [ "$status" = "Succeeded" ]; then
    location=$(echo "$status_response" | jq -r '.resourceLocation // empty')
    def_response=$(curl -s -X GET "$location" -H "Authorization: Bearer $ACCESS_TOKEN")
    definition=$(echo "$def_response" | jq -r '.definition.parts[0].payload')
    break
  elif [ "$status" = "Failed" ]; then
    echo "❌ Failed to get definition"; exit 1
  fi
done

echo "📤 Creating cloned notebook..."

# Create new notebook
create_body=$(jq -n --arg name "$new_name" '{displayName: $name, type: "Notebook"}')

create_response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$target_workspace/items" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$create_body")

if [ "$(echo "$create_response" | tail -n1)" != "201" ] && [ "$(echo "$create_response" | tail -n1)" != "202" ]; then
  echo "❌ Failed to create notebook"; exit 1
fi

new_notebook_id=$(echo "$create_response" | head -n-1 | jq -r '.id')

# Apply definition
update_body=$(jq -n --arg payload "$definition" \
  '{definition: {parts: [{path: "notebook-content.py", payload: $payload, payloadType: "InlineBase64"}]}}')

update_response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$target_workspace/notebooks/$new_notebook_id/updateDefinition" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$update_body")

if [ "$(echo "$update_response" | tail -n1)" != "202" ]; then
  echo "❌ Failed to update definition"; exit 1
fi

echo "⏳ Finalizing clone..."
sleep 5

echo "✅ Notebook cloned successfully"
echo ""
echo "Source:     $notebook_id"
echo "Clone:      $new_notebook_id"
echo "Clone Name: $new_name"
echo ""
echo "💡 View: /fabric:get-notebook $target_workspace $new_notebook_id"
```

## Use Cases

### Quick Duplicate
```bash
/fabric:clone-notebook <ws-id> <nb-id> "Copy of Analysis"
```

### Cross-Workspace Clone
```bash
/fabric:clone-notebook <dev-ws> <nb-id> "Prod Analysis" --target-workspace <prod-ws>
```

## API Reference
- **Get Definition**: `POST .../notebooks/{id}/getDefinition` (LRO)
- **Create**: `POST .../items`
- **Update**: `POST .../notebooks/{id}/updateDefinition` (LRO)
