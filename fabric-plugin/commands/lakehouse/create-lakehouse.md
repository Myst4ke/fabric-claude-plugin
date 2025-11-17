---
description: Create a new lakehouse
argument-hint: <workspace-id> <name> [--description <desc>]
---

# /fabric:create-lakehouse

## Purpose
Create a new Fabric lakehouse for Delta Lake tables and files.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `name`: Required. Lakehouse name (1-256 characters)
- `--description <desc>`: Optional. Description

## Instructions

```bash
workspace_id="$1"
lakehouse_name="$2"
description=""

shift 2
while [[ $# -gt 0 ]]; do
  case $1 in
    --description) description="$2"; shift 2 ;;
    *) echo "❌ Unknown argument: $1"; exit 1 ;;
  esac
done

if [ -z "$workspace_id" ] || [ -z "$lakehouse_name" ]; then
  echo "❌ Workspace ID and name required"; exit 1
fi

if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid workspace ID"; exit 1
fi

if [ ${#lakehouse_name} -lt 1 ] || [ ${#lakehouse_name} -gt 256 ]; then
  echo "❌ Name must be 1-256 characters"; exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "🏞️  Creating lakehouse..."

if [ -n "$description" ]; then
  request_body=$(jq -n --arg name "$lakehouse_name" --arg desc "$description" \
    '{displayName: $name, description: $desc, type: "Lakehouse"}')
else
  request_body=$(jq -n --arg name "$lakehouse_name" '{displayName: $name, type: "Lakehouse"}')
fi

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$request_body")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" = "201" ] || [ "$http_code" = "202" ]; then
  lakehouse_id=$(echo "$response_body" | jq -r '.id')

  if [ "$http_code" = "202" ]; then
    echo "⏳ Lakehouse creation in progress..."
    operation_id=$(echo "$response" | grep -i "^x-ms-operation-id:" | cut -d' ' -f2 | tr -d '\r')

    for ((i=0; i<30; i++)); do
      sleep 2
      op_response=$(curl -s -X GET "https://api.fabric.microsoft.com/v1/operations/$operation_id" \
        -H "Authorization: Bearer $ACCESS_TOKEN")
      op_status=$(echo "$op_response" | jq -r '.status')

      if [ "$op_status" = "Succeeded" ]; then
        lakehouse_id=$(echo "$op_response" | jq -r '.resourceId')
        break
      elif [ "$op_status" = "Failed" ]; then
        echo "❌ Creation failed"; exit 1
      fi
    done
  fi

  echo "✅ Lakehouse created"
  echo ""
  echo "Name:         $lakehouse_name"
  echo "Lakehouse ID: $lakehouse_id"
  echo "Workspace ID: $workspace_id"
  echo ""
  echo "💡 Next steps:"
  echo "  • View: /fabric:get-lakehouse $workspace_id $lakehouse_id"
  echo "  • List tables: /fabric:list-lakehouse-tables $workspace_id $lakehouse_id"
  echo "  • Upload files: /fabric:upload-file $workspace_id $lakehouse_id <path> <file>"

else
  echo "❌ Failed (HTTP $http_code)"; exit 1
fi
```

## API Reference
- **Endpoint**: `POST .../items` with type: "Lakehouse"
- **Response**: 201 Created or 202 Accepted (LRO)
- **Permissions**: Contributor, Member, or Admin
