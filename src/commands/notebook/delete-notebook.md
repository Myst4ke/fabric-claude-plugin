---
description: Delete a notebook
argument-hint: <workspace-id> <notebook-id> [--force]
---

# /fabric:delete-notebook

## Purpose
Permanently delete a Fabric notebook from a workspace. Requires confirmation unless --force flag is used.

## Arguments
- `workspace-id`: Required. GUID of the workspace
- `notebook-id`: Required. GUID of the notebook
- `--force`: Optional. Skip confirmation prompt

## Instructions

```bash
workspace_id="$1"
notebook_id="$2"
force_delete=false

# Parse optional force flag
shift 2
while [[ $# -gt 0 ]]; do
  case $1 in
    --force)
      force_delete=true
      shift
      ;;
    *)
      echo "❌ Unknown argument: $1"
      echo "Usage: /fabric:delete-notebook <workspace-id> <notebook-id> [--force]"
      exit 1
      ;;
  esac
done

if [ -z "$workspace_id" ] || [ -z "$notebook_id" ]; then
  echo "❌ Workspace ID and notebook ID are required"
  echo "Usage: /fabric:delete-notebook <workspace-id> <notebook-id> [--force]"
  exit 1
fi

# Validate GUIDs
if ! [[ "$workspace_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid workspace ID format (must be GUID)"
  exit 1
fi

if ! [[ "$notebook_id" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  echo "❌ Invalid notebook ID format (must be GUID)"
  exit 1
fi

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

# Get notebook details before deletion
echo "📓 Fetching notebook details..."

get_response=$(curl -s -w "\n%{http_code}" -X GET \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items/$notebook_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

get_http_code=$(echo "$get_response" | tail -n1)
get_body=$(echo "$get_response" | head -n-1)

if [ "$get_http_code" != "200" ]; then
  echo "❌ Notebook not found or inaccessible (HTTP $get_http_code)"
  error_msg=$(echo "$get_body" | jq -r '.error.message // "Unknown error"')
  echo "Error: $error_msg"
  echo ""
  echo "💡 List notebooks: /fabric:list-notebooks $workspace_id"
  exit 1
fi

notebook_name=$(echo "$get_body" | jq -r '.displayName')
notebook_desc=$(echo "$get_body" | jq -r '.description // "No description"')

# Show notebook details
echo ""
echo "Notebook to be deleted:"
echo "══════════════════════════════════════════════════════════"
echo "Name:        $notebook_name"
echo "ID:          $notebook_id"
echo "Description: $notebook_desc"
echo "══════════════════════════════════════════════════════════"
echo ""

# Confirmation prompt unless --force
if [ "$force_delete" = false ]; then
  echo "⚠️  This action cannot be undone."
  echo "   All notebook cells, code, and outputs will be permanently lost."
  echo ""
  read -p "Type 'DELETE' to confirm: " confirmation

  if [ "$confirmation" != "DELETE" ]; then
    echo "❌ Deletion cancelled"
    exit 0
  fi
  echo ""
fi

echo "🗑️  Deleting notebook..."

response=$(curl -s -w "\n%{http_code}" -X DELETE \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/items/$notebook_id" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "200" ] || [ "$http_code" = "204" ]; then
  echo "✅ Notebook deleted successfully"
  echo ""
  echo "The notebook \"$notebook_name\" has been permanently removed."
  echo ""
  echo "💡 Next steps:"
  echo "  • View remaining notebooks: /fabric:list-notebooks $workspace_id"
  echo "  • Create new notebook: /fabric:create-notebook $workspace_id \"New Notebook\""
  echo ""
  echo "⚠️  Note: This action cannot be undone. If you need to recover:"
  echo "   • Check if you have backup exports"
  echo "   • Review workspace snapshots (if available)"

else
  echo "❌ Failed to delete notebook (HTTP $http_code)"
  response_body=$(echo "$response" | head -n-1)
  error_msg=$(echo "$response_body" | jq -r '.error.message // "Unknown error"')
  echo "Error: $error_msg"
  exit 1
fi
```

## Safety Features

### Confirmation Prompt
By default, requires typing 'DELETE':
```
Notebook to be deleted:
══════════════════════════════════════════════════════════
Name:        Sales Analysis
ID:          abc123-def456-ghi789
Description: Monthly sales data analysis
══════════════════════════════════════════════════════════

⚠️  This action cannot be undone.
   All notebook cells, code, and outputs will be permanently lost.

Type 'DELETE' to confirm: DELETE
```

### Force Flag
Skip confirmation for automation:
```bash
/fabric:delete-notebook <workspace-id> <notebook-id> --force
```

## Use Cases

### Remove Test Notebooks
```bash
# Delete temporary notebook
/fabric:delete-notebook <workspace-id> <notebook-id>
```

### Clean Up Old Notebooks
```bash
# List and selectively delete
/fabric:list-notebooks <workspace-id>

# Delete specific notebook
/fabric:delete-notebook <workspace-id> <notebook-id>
```

### Automation Script
```bash
# Delete with force flag
/fabric:delete-notebook <workspace-id> <notebook-id> --force
```

## What Happens When Deleted

**Permanently Removed:**
- Notebook metadata (name, description)
- All cells and code
- Cell outputs and visualizations
- Execution history
- Notebook configuration

**Not Affected:**
- Workspace
- Other notebooks
- Lakehouses or data sources used by notebook
- Scheduled jobs (if any) - may need manual cleanup

## Important Notes

### Cannot Be Undone
- Deletion is permanent
- No "trash" or "recycle bin"
- Must recreate if deleted by mistake
- Consider backup before deletion

### Before Deleting

**Recommended Actions:**
1. Export notebook: `/fabric:export-notebook <ws-id> <notebook-id>`
2. Check for dependencies
3. Review execution history
4. Verify no scheduled jobs depend on it

### Alternative: Export Instead

If you might need the notebook later:
```bash
# Export for backup
/fabric:export-notebook <workspace-id> <notebook-id> backup.ipynb

# Can be re-imported later
/fabric:import-notebook <workspace-id> backup.ipynb
```

## Related Commands
- `/fabric:list-notebooks <workspace-id>` - List all notebooks
- `/fabric:get-notebook <workspace-id> <notebook-id>` - View details
- `/fabric:export-notebook <workspace-id> <notebook-id>` - Backup before deleting
- `/fabric:create-notebook <workspace-id> <name>` - Create new notebook

## API Reference
- **Endpoint**: `DELETE https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{itemId}`
- **Response**: 200 OK or 204 No Content
- **Permissions**: Contributor, Member, or Admin role

## Best Practices

1. **Always Export First**: Create backup before deletion
2. **Review Details**: Confirm you're deleting the correct notebook
3. **Check Dependencies**: Verify no pipelines or jobs depend on it
4. **Document Deletions**: Note why notebook was deleted
5. **Use Force Carefully**: Only in automated scripts with proper checks

## Error Scenarios

### Notebook Not Found (404)
```
❌ Notebook not found or inaccessible
```
**Solution**: Verify notebook ID with `/fabric:list-notebooks`

### Permission Denied (403)
```
❌ Failed to delete notebook (HTTP 403)
Error: Insufficient privileges
```
**Solution**: Requires Contributor, Member, or Admin role

### Notebook In Use
Some notebooks cannot be deleted if:
- Currently executing
- Part of active deployment

**Solution**: Wait for execution to complete or cancel it first
