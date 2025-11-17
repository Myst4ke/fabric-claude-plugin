---
description: Export notebook to .ipynb file
argument-hint: <workspace-id> <notebook-id> <output-file>
---

# /fabric:export-notebook

## Purpose
Export notebook definition to .ipynb file for backup, version control, or migration.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `notebook-id`: Required. GUID of the notebook
- `output-file`: Required. Path for exported .ipynb file

## Instructions

```bash
workspace_id="$1"
notebook_id="$2"
output_file="$3"

if [ -z "$workspace_id" ] || [ -z "$notebook_id" ] || [ -z "$output_file" ]; then
  echo "❌ All arguments required"
  exit 1
fi

if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid workspace ID"; exit 1
fi

if ! [[ "$notebook_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid notebook ID"; exit 1
fi

if [ -f "$output_file" ]; then
  read -p "⚠️  File exists. Overwrite? (y/N): " confirm
  if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "❌ Export cancelled"; exit 0
  fi
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

echo "📥 Requesting notebook definition..."

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/notebooks/$notebook_id/getDefinition" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)

if [ "$http_code" != "202" ]; then
  echo "❌ Failed (HTTP $http_code)"; exit 1
fi

operation_id=$(echo "$response" | grep -i "^x-ms-operation-id:" | cut -d' ' -f2 | tr -d '\r')
echo "⏳ Retrieving definition..."

for ((i=0; i<60; i++)); do
  sleep 3

  status_response=$(curl -s -X GET \
    "https://api.fabric.microsoft.com/v1/operations/$operation_id" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  status=$(echo "$status_response" | jq -r '.status')

  if [ "$status" = "Succeeded" ]; then
    location=$(echo "$status_response" | jq -r '.resourceLocation // empty')

    def_response=$(curl -s -X GET "$location" -H "Authorization: Bearer $ACCESS_TOKEN")
    definition=$(echo "$def_response" | jq -r '.definition.parts[0].payload')

    echo "$definition" | base64 -d > "$output_file"

    file_size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null)
    file_size_kb=$((file_size / 1024))

    echo "✅ Notebook exported successfully"
    echo ""
    echo "Output File: $output_file"
    echo "File Size:   ${file_size_kb} KB"
    echo ""
    echo "💡 Next steps:"
    echo "  • View: cat $output_file | jq ."
    echo "  • Import: /fabric:import-notebook <workspace-id> $output_file"
    echo "  • Version control: git add $output_file"
    exit 0
  elif [ "$status" = "Failed" ]; then
    echo "❌ Failed"; exit 1
  fi
done

echo "❌ Timeout"; exit 1
```

## Use Cases

### Backup
```bash
# Export before changes
/fabric:export-notebook <ws-id> <nb-id> "backup-$(date +%Y%m%d).ipynb"
```

### Version Control
```bash
# Export to git repo
/fabric:export-notebook <ws-id> <nb-id> "notebooks/analysis.ipynb"
git add notebooks/analysis.ipynb
git commit -m "Update analysis notebook"
```

### Migration
```bash
# Export from dev
/fabric:export-notebook <dev-ws> <nb-id> notebook.ipynb

# Import to prod
/fabric:import-notebook <prod-ws> notebook.ipynb
```

## API Reference
- **Endpoint**: `POST .../notebooks/{id}/getDefinition` (LRO)
- **Format**: Standard Jupyter .ipynb format
- **Permissions**: Any workspace role
