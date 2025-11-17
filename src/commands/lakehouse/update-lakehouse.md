---
description: Update lakehouse metadata
argument-hint: <workspace-id> <lakehouse-id> [--name <name>] [--description <desc>]
---

# /fabric:update-lakehouse

## Purpose
Update lakehouse name and/or description.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `lakehouse-id`: Required. GUID of the lakehouse
- `--name <name>`: Optional. New name
- `--description <desc>`: Optional. New description

## Instructions

```bash
workspace_id="$1"
lakehouse_id="$2"
new_name=""
new_description=""

shift 2
while [[ $# -gt 0 ]]; do
  case $1 in
    --name) new_name="$2"; shift 2 ;;
    --description) new_description="$2"; shift 2 ;;
    *) echo "❌ Unknown argument: $1"; exit 1 ;;
  esac
done

if [ -z "$workspace_id" ] || [ -z "$lakehouse_id" ]; then
  echo "❌ Both IDs required"; exit 1
fi

if [ -z "$new_name" ] && [ -z "$new_description" ]; then
  echo "❌ At least one field required"; exit 1
fi

if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]] || \
   ! [[ "$lakehouse_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid ID format"; exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

request_body="{"
first=true

if [ -n "$new_name" ]; then
  request_body="$request_body\"displayName\":\"$new_name\""
  first=false
fi

if [ -n "$new_description" ]; then
  [ "$first" = false ] && request_body="$request_body,"
  request_body="$request_body\"description\":\"$new_description\""
fi

request_body="$request_body}"

response=$(curl -s -w "\n%{http_code}" -X PATCH \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/lakehouses/$lakehouse_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$request_body")

if [ "$(echo "$response" | tail -n1)" = "200" ]; then
  echo "✅ Lakehouse updated"
else
  echo "❌ Failed"; exit 1
fi
```

## API Reference
- **Endpoint**: `PATCH .../lakehouses/{id}`
- **Response**: 200 OK
- **Permissions**: Contributor, Member, or Admin
