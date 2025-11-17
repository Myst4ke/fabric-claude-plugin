---
description: Delete a table from lakehouse
argument-hint: <workspace-id> <lakehouse-id> <table-name> [--force]
---

# /fabric:delete-table

## Purpose
Delete a table and its data from the lakehouse.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `lakehouse-id`: Required. GUID of the lakehouse
- `table-name`: Required. Table name to delete
- `--force`: Optional. Skip confirmation

## Instructions

```bash
workspace_id="$1"
lakehouse_id="$2"
table_name="$3"
force=false

shift 3
while [[ $# -gt 0 ]]; do
  case $1 in
    --force) force=true; shift ;;
    *) echo "❌ Unknown argument: $1"; exit 1 ;;
  esac
done

if [ -z "$workspace_id" ] || [ -z "$lakehouse_id" ] || [ -z "$table_name" ]; then
  echo "❌ All arguments required"; exit 1
fi

if [ "$force" = false ]; then
  echo "⚠️  Delete table '$table_name' and all its data?"
  read -p "Type 'DELETE' to confirm: " confirmation
  if [ "$confirmation" != "DELETE" ]; then
    echo "❌ Cancelled"; exit 0
  fi
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

response=$(curl -s -w "\n%{http_code}" -X DELETE \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/lakehouses/$lakehouse_id/tables/$table_name" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if [ "$(echo "$response" | tail -n1)" = "200" ] || [ "$(echo "$response" | tail -n1)" = "204" ]; then
  echo "✅ Table deleted: $table_name"
else
  echo "❌ Failed"; exit 1
fi
```

## API Reference
- **Endpoint**: `DELETE .../lakehouses/{id}/tables/{tableName}`
- **Response**: 200 OK or 204 No Content
- **Permissions**: Contributor, Member, or Admin
