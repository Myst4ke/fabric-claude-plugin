---
description: Delete file from lakehouse
argument-hint: <workspace-id> <lakehouse-id> <file-path> [--force]
---

# /fabric:delete-file

## Purpose
Delete a file from lakehouse file storage.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `lakehouse-id`: Required. GUID of the lakehouse
- `file-path`: Required. Path to file in lakehouse
- `--force`: Optional. Skip confirmation

## Instructions

```bash
workspace_id="$1"
lakehouse_id="$2"
file_path="$3"
force=false

shift 3
while [[ $# -gt 0 ]]; do
  case $1 in
    --force) force=true; shift ;;
    *) echo "❌ Unknown argument: $1"; exit 1 ;;
  esac
done

if [ -z "$workspace_id" ] || [ -z "$lakehouse_id" ] || [ -z "$file_path" ]; then
  echo "❌ All arguments required"; exit 1
fi

if [ "$force" = false ]; then
  echo "⚠️  Delete file: $file_path"
  read -p "Type 'DELETE' to confirm: " confirmation
  if [ "$confirmation" != "DELETE" ]; then
    echo "❌ Cancelled"; exit 0
  fi
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

response=$(curl -s -w "\n%{http_code}" -X DELETE \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/lakehouses/$lakehouse_id/files/$file_path" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "200" ] || [ "$http_code" = "204" ]; then
  echo "✅ File deleted: $file_path"
else
  echo "❌ Failed (HTTP $http_code)"; exit 1
fi
```

## Use Cases

### Delete Single File
```bash
/fabric:delete-file <ws-id> <lh-id> "data/old-data.csv"
```

### Batch Delete
```bash
for file in $(list_old_files); do
  /fabric:delete-file <ws-id> <lh-id> "$file" --force
done
```

## API Reference
- **Endpoint**: `DELETE .../lakehouses/{id}/files/{path}`
- **Response**: 200 OK or 204 No Content
- **Permissions**: Contributor, Member, or Admin
