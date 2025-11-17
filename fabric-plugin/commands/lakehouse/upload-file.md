---
description: Upload file to lakehouse
argument-hint: <workspace-id> <lakehouse-id> <target-path> <local-file>
---

# /fabric:upload-file

## Purpose
Upload a file to lakehouse file storage.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `lakehouse-id`: Required. GUID of the lakehouse
- `target-path`: Required. Target path in lakehouse
- `local-file`: Required. Local file to upload

## Instructions

```bash
workspace_id="$1"
lakehouse_id="$2"
target_path="$3"
local_file="$4"

if [ -z "$workspace_id" ] || [ -z "$lakehouse_id" ] || [ -z "$target_path" ] || [ -z "$local_file" ]; then
  echo "❌ All arguments required"; exit 1
fi

if [ ! -f "$local_file" ]; then
  echo "❌ File not found: $local_file"; exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📤 Uploading file..."

file_size=$(stat -f%z "$local_file" 2>/dev/null || stat -c%s "$local_file" 2>/dev/null)
file_size_kb=$((file_size / 1024))

echo "   File: $local_file ($file_size_kb KB)"
echo "   Target: $target_path"

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/lakehouses/$lakehouse_id/files" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/octet-stream" \
  -F "path=$target_path" \
  -F "file=@$local_file")

http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "201" ] || [ "$http_code" = "200" ]; then
  echo "✅ File uploaded successfully"
  echo ""
  echo "💡 View: /fabric:list-lakehouse-files $workspace_id $lakehouse_id"
else
  echo "❌ Upload failed (HTTP $http_code)"; exit 1
fi
```

## Use Cases

### Upload Data File
```bash
/fabric:upload-file <ws-id> <lh-id> "data/sales.csv" "./local/sales.csv"
```

### Upload Multiple Files
```bash
for file in data/*.csv; do
  /fabric:upload-file <ws-id> <lh-id> "data/$(basename $file)" "$file"
done
```

## API Reference
- **Endpoint**: `POST .../lakehouses/{id}/files`
- **Response**: 201 Created
- **Permissions**: Contributor, Member, or Admin
