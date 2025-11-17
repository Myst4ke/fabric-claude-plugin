---
description: List files in lakehouse
argument-hint: <workspace-id> <lakehouse-id> [--path <folder-path>]
---

# /fabric:list-lakehouse-files

## Purpose
List files stored in lakehouse file section.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `lakehouse-id`: Required. GUID of the lakehouse
- `--path <folder>`: Optional. Folder path (default: root)

## Instructions

```bash
workspace_id="$1"
lakehouse_id="$2"
folder_path=""

shift 2
while [[ $# -gt 0 ]]; do
  case $1 in
    --path) folder_path="$2"; shift 2 ;;
    *) echo "❌ Unknown argument: $1"; exit 1 ;;
  esac
done

if [ -z "$workspace_id" ] || [ -z "$lakehouse_id" ]; then
  echo "❌ Both IDs required"; exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📁 Listing files..."

if [ -n "$folder_path" ]; then
  endpoint="https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/lakehouses/$lakehouse_id/files?path=$folder_path"
else
  endpoint="https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/lakehouses/$lakehouse_id/files"
fi

response=$(curl -s -w "\n%{http_code}" -X GET "$endpoint" -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
  files=$(echo "$response_body" | jq '.value')
  count=$(echo "$files" | jq 'length')

  echo "✅ Found $count file(s)"
  echo ""

  if [ "$count" -eq 0 ]; then
    echo "No files found."
    echo ""
    echo "💡 Upload: /fabric:upload-file $workspace_id $lakehouse_id <path> <local-file>"
    exit 0
  fi

  echo "$files" | jq -r '.[] | "  \(.name) (\(.size) bytes)"'
else
  echo "❌ Failed (HTTP $http_code)"; exit 1
fi
```

## API Reference
- **Endpoint**: `GET .../lakehouses/{id}/files`
- **Response**: 200 OK
- **Permissions**: Any workspace role
