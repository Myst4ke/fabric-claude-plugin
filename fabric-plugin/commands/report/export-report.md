---
description: Export a report
argument-hint: <workspace-id> <report-id> <output-file> [--format PDF|PPTX]
---

# /fabric:export-report

## Instructions

```bash
workspace_id="$1"
report_id="$2"
output_file="$3"
format="PDF"

shift 3
while [[ $# -gt 0 ]]; do
  case $1 in
    --format) format="$2"; shift 2 ;;
    *) echo "❌ Unknown: $1"; exit 1 ;;
  esac
done

[ -z "$workspace_id" ] || [ -z "$report_id" ] || [ -z "$output_file" ] && echo "❌ All required" && exit 1

echo "🔐 Authenticating..."
ACCESS_TOKEN=$(fabric_auth_skill)

body=$(jq -n --arg f "$format" '{format:$f}')

response=$(curl -s -w "\n%{http_code}" -X POST \
  "https://api.fabric.microsoft.com/v1/workspaces/$workspace_id/reports/$report_id/export" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$body")

[ "$(echo "$response" | tail -n1)" = "200" ] && echo "$response" | head -n-1 > "$output_file" && echo "✅ Exported: $output_file" || echo "❌ Failed"
```

## API Reference
- **Endpoint**: `POST .../reports/{id}/export`
- **Formats**: PDF, PPTX
- **Permissions**: Any workspace role
