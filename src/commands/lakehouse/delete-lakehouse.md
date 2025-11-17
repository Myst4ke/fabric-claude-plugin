---
description: Delete a lakehouse
argument-hint: <workspace-id> <lakehouse-id> [--force]
---

# /fabric:delete-lakehouse

## Purpose
Permanently delete a lakehouse including all tables and files.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `lakehouse-id`: Required. GUID of the lakehouse
- `--force`: Optional. Skip confirmation

## Instructions

```bash
workspace_id="$1"
lakehouse_id="$2"
force=false

shift 2
while [[ $# -gt 0 ]]; do
  case $1 in
    --force) force=true; shift ;;
    *) echo "❌ Unknown argument: $1"; exit 1 ;;
  esac
done

if [ -z "$workspace_id" ] || [ -z "$lakehouse_id" ]; then
  echo "❌ Both IDs required"; exit 1
fi

if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]] || \
   ! [[ "$lakehouse_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid ID format"; exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

get_response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/lakehouses/$lakehouse_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if [ "$(echo "$get_response" | tail -n1)" != "200" ]; then
  echo "❌ Lakehouse not found"; exit 1
fi

name=$(echo "$get_response" | head -n-1 | jq -r '.displayName')

echo ""
echo "Lakehouse to be deleted:"
echo "══════════════════════════════════════════════════════════"
echo "Name: $name"
echo "ID:   $lakehouse_id"
echo "══════════════════════════════════════════════════════════"
echo ""

if [ "$force" = false ]; then
  echo "⚠️  This will permanently delete ALL tables and files."
  echo ""
  read -p "Type 'DELETE' to confirm: " confirmation

  if [ "$confirmation" != "DELETE" ]; then
    echo "❌ Deletion cancelled"; exit 0
  fi
fi

response=$(curl -s -w "\n%{http_code}" -X DELETE \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/lakehouses/$lakehouse_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if [ "$(echo "$response" | tail -n1)" = "200" ] || [ "$(echo "$response" | tail -n1)" = "204" ]; then
  echo "✅ Lakehouse deleted"
else
  echo "❌ Failed"; exit 1
fi
```

## API Reference
- **Endpoint**: `DELETE .../lakehouses/{id}`
- **Response**: 200 OK or 204 No Content
- **Permissions**: Contributor, Member, or Admin

## Warning
Deletes all tables, files, and data permanently.
