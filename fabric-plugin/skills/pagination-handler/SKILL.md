---
name: pagination-handler
description: Handle Microsoft Fabric API pagination for list operations with continuationToken
---

# Pagination Handler Skill

## Purpose
Manage paginated responses from Microsoft Fabric API list operations. This skill automatically fetches all pages of results or implements streaming pagination with user control, handling continuationToken and continuationUri patterns.

## When to Use
- All list operations (workspaces, items, users, etc.)
- When API response contains `continuationToken` or `continuationUri`
- When result sets may exceed single-page limits (~100 items)

**Common Paginated Operations:**
- List workspaces
- List items in a workspace
- List users/role assignments
- List files in lakehouse
- List tables in lakehouse
- List schedules, jobs, refreshes, etc.

## Prerequisites
- Initial API response with pagination metadata
- Valid access token for subsequent requests
- Understanding of desired pagination behavior (fetch all vs. stream)

## Implementation Steps

### 1. Detect Paginated Response
Check if API response contains pagination indicators:

**Response Structure:**
```json
{
  "value": [
    { "id": "item1", "name": "First Item" },
    { "id": "item2", "name": "Second Item" },
    ...
  ],
  "continuationToken": "eyJjdCI6MTY5OTk5OTk5OX0=",
  "continuationUri": "https://api.fabric.microsoft.com/v1/workspaces?continuationToken=eyJjdCI6MTY5OTk5OTk5OX0="
}
```

**Key Fields:**
- `value`: Array of results for current page
- `continuationToken`: Token to fetch next page (null/absent when no more pages)
- `continuationUri`: Direct URL for next page (optional, not always provided)

### 2. Choose Pagination Strategy

#### Strategy A: Fetch All Pages (Default)
**Use when:**
- Total results expected to be reasonable (<1000 items)
- Need complete dataset for processing
- User wants comprehensive view

**Example:**
```bash
/fabric:list-workspaces --all
# Fetches all pages automatically
```

#### Strategy B: Streaming Pagination
**Use when:**
- Large result sets (>1000 items)
- Want to display results progressively
- Memory-conscious operations

**Example:**
```bash
/fabric:list-items my-workspace --stream
# Displays results as they're fetched, page by page
```

#### Strategy C: Manual Pagination
**Use when:**
- User wants control over page fetching
- Interactive exploration
- Large datasets where user may not need all results

**Example:**
```bash
/fabric:list-items my-workspace --page-size 50
# Shows first 50 items with option to fetch more
```

### 3. Implement Fetch-All Pagination

**Algorithm:**
```bash
fetch_all_pages() {
  endpoint=$1
  access_token=$2

  all_results=[]
  continuation_token=""
  page_count=0
  total_items=0

  while true; do
    page_count=$((page_count + 1))

    # Construct URL with continuation token if present
    if [ -n "$continuation_token" ]; then
      url="${endpoint}?continuationToken=${continuation_token}"
    else
      url="$endpoint"
    fi

    # Fetch page
    response=$(curl -s -X GET "$url" \
      -H "Authorization: Bearer $access_token")

    # Extract results from this page
    page_results=$(echo "$response" | jq -r '.value')
    page_size=$(echo "$page_results" | jq 'length')
    total_items=$((total_items + page_size))

    # Append to all results
    all_results=$(echo "$all_results $page_results" | jq -s 'add')

    # Display progress
    echo "📄 Fetched page $page_count ($page_size items, $total_items total)..."

    # Check for more pages
    continuation_token=$(echo "$response" | jq -r '.continuationToken // empty')

    if [ -z "$continuation_token" ] || [ "$continuation_token" = "null" ]; then
      echo "✅ Fetched all pages ($page_count pages, $total_items items)"
      break
    fi

    # Rate limiting: small delay between pages
    sleep 0.5
  done

  # Return combined results
  echo "$all_results"
}
```

**Progress Display:**
```
📄 Fetching workspaces...
📄 Fetched page 1 (100 items, 100 total)...
📄 Fetched page 2 (100 items, 200 total)...
📄 Fetched page 3 (47 items, 247 total)...
✅ Fetched all pages (3 pages, 247 items)

Total workspaces found: 247
```

### 4. Implement Streaming Pagination

**Algorithm:**
```bash
stream_pages() {
  endpoint=$1
  access_token=$2
  processor_function=$3  # Function to process each page

  continuation_token=""
  page_count=0

  while true; do
    page_count=$((page_count + 1))

    # Construct URL
    if [ -n "$continuation_token" ]; then
      url="${endpoint}?continuationToken=${continuation_token}"
    else
      url="$endpoint"
    fi

    # Fetch page
    response=$(curl -s -X GET "$url" \
      -H "Authorization: Bearer $access_token")

    # Extract and process this page immediately
    page_results=$(echo "$response" | jq -r '.value')

    # Call processor function with this page
    $processor_function "$page_results"

    # Check for more pages
    continuation_token=$(echo "$response" | jq -r '.continuationToken // empty')

    if [ -z "$continuation_token" ] || [ "$continuation_token" = "null" ]; then
      break
    fi

    sleep 0.5
  done
}

# Example processor function
display_workspace_page() {
  page_data=$1

  echo "$page_data" | jq -r '.[] | "\(.name) (\(.id))"'
}

# Usage
stream_pages "https://api.fabric.microsoft.com/v1/workspaces" "$token" display_workspace_page
```

**Output:**
```
Dev Workspace (abc-123)
Test Workspace (def-456)
Prod Workspace (ghi-789)
...
Analytics Workspace (jkl-012)

Page 1 complete. Fetching more...

Finance Workspace (mno-345)
HR Workspace (pqr-678)
...
```

### 5. Implement Manual Pagination

**Interactive Algorithm:**
```bash
manual_pagination() {
  endpoint=$1
  access_token=$2

  continuation_token=""
  page_count=0

  while true; do
    page_count=$((page_count + 1))

    # Construct URL
    if [ -n "$continuation_token" ]; then
      url="${endpoint}?continuationToken=${continuation_token}"
    else
      url="$endpoint"
    fi

    # Fetch page
    response=$(curl -s -X GET "$url" \
      -H "Authorization: Bearer $access_token")

    # Display this page
    echo "$response" | jq -r '.value[] | "\(.name) - \(.id)"'

    # Check for more pages
    continuation_token=$(echo "$response" | jq -r '.continuationToken // empty')

    if [ -z "$continuation_token" ] || [ "$continuation_token" = "null" ]; then
      echo ""
      echo "✅ No more results"
      break
    fi

    # Ask user if they want more
    echo ""
    echo "📄 Page $page_count complete. More results available."
    echo "Fetch next page? (y/n/a for yes/no/all)"
    read -r response

    case "$response" in
      y|Y)
        echo "Fetching next page..."
        continue
        ;;
      a|A)
        echo "Fetching all remaining pages..."
        # Switch to fetch-all mode
        fetch_all_remaining "$url" "$access_token" "$continuation_token"
        break
        ;;
      *)
        echo "✅ Stopped pagination"
        break
        ;;
    esac
  done
}
```

### 6. Handle Edge Cases

#### Case 1: Empty Results
```json
{
  "value": [],
  "continuationToken": null
}
```
**Display:**
```
ℹ️ No items found

The workspace is empty or you don't have permission to view items.
```

#### Case 2: Single Page (No Continuation)
```json
{
  "value": [ ... 12 items ... ]
  // No continuationToken field
}
```
**Display:**
```
✅ Found 12 workspaces (1 page)

[Display items in table format]
```

#### Case 3: continuationUri vs continuationToken
Some endpoints provide `continuationUri` (full URL) instead of token:

**Prefer continuationUri if available:**
```bash
if [ -n "$continuation_uri" ]; then
  next_url="$continuation_uri"
elif [ -n "$continuation_token" ]; then
  next_url="${base_endpoint}?continuationToken=${continuation_token}"
fi
```

#### Case 4: Malformed Continuation Token
If continuation token is invalid:
```
❌ Invalid continuation token

The pagination token has expired or is malformed.

Actions:
• Restart the list operation from the beginning
• This can happen if tokens expire (typically after 10-15 minutes)

Starting fresh query...
```

#### Case 5: Network Error Mid-Pagination
Apply error-handler retry logic:
```
⚠️ Network error on page 5 of pagination

Retrying page fetch (attempt 1 of 3)...
```
Retry same page, don't lose progress.

### 7. Optimize Performance

#### Concurrent Page Fetching (Advanced)
For very large datasets, fetch multiple pages concurrently:
```bash
# NOT RECOMMENDED for initial implementation
# Fabric API may have rate limits
# Only use if API documentation confirms support

fetch_pages_concurrently() {
  # Queue multiple continuation tokens
  # Fetch 3-5 pages in parallel
  # Reassemble in correct order
}
```

#### Result Caching
Cache paginated results for repeated queries:
```bash
# Cache key: endpoint + query params + timestamp
cache_key=$(echo "${endpoint}${params}" | md5sum | cut -d' ' -f1)
cache_file="/tmp/fabric_cache_${cache_key}.json"

if [ -f "$cache_file" ]; then
  cache_age=$(($(date +%s) - $(stat -c %Y "$cache_file")))
  if [ $cache_age -lt 300 ]; then
    echo "📦 Using cached results (${cache_age}s old)..."
    cat "$cache_file"
    return
  fi
fi

# Fetch fresh data and cache it
results=$(fetch_all_pages "$endpoint" "$token")
echo "$results" > "$cache_file"
```

### 8. Format Output for Large Result Sets

#### Table Format with Pagination
```bash
# Display first page in table
echo "$page_results" | jq -r '
  ["NAME", "ID", "TYPE", "CAPACITY"],
  (.[] | [.displayName, .id, .type, .capacityId]),
  | @tsv
' | column -t -s $'\t'

# Output:
NAME                ID                                    TYPE        CAPACITY
Dev Workspace       abc-123-def-456                       Workspace   cap-001
Test Workspace      ghi-789-jkl-012                       Workspace   cap-001
...
```

#### Summary Mode for Large Sets
```bash
# For >500 items, show summary + sample
if [ $total_items -gt 500 ]; then
  echo "✅ Found $total_items items (showing first 100)"
  echo ""
  echo "$all_results" | jq -r '.[:100][] | "\(.name) - \(.id)"'
  echo ""
  echo "... and $((total_items - 100)) more items"
  echo ""
  echo "Use --export to save all results to file"
fi
```

### 9. Export Pagination Results

**Export to JSON:**
```bash
/fabric:list-workspaces --export workspaces.json

# Output:
📄 Fetching all workspaces...
📄 Fetched page 1 (100 items)...
📄 Fetched page 2 (100 items)...
📄 Fetched page 3 (47 items)...
✅ Exported 247 workspaces to workspaces.json
```

**Export to CSV:**
```bash
/fabric:list-items my-workspace --export items.csv

# Convert JSON to CSV
echo "$all_results" | jq -r '
  ["Name", "ID", "Type", "Created"],
  (.[] | [.displayName, .id, .type, .createdDateTime])
  | @csv
' > items.csv
```

## Input Parameters
- `endpoint`: String (base API endpoint URL)
- `access_token`: String (Bearer token)
- `pagination_mode`: String ("all" | "stream" | "manual")
- `page_processor`: Function (optional, for streaming mode)

## Output
- **Fetch-All Mode**: Array of all items across all pages
- **Streaming Mode**: Yields pages progressively
- **Manual Mode**: Interactive page-by-page display

## Performance Considerations
1. **Memory usage**: Fetch-all stores entire result set in memory
2. **API rate limits**: ~100 items per page, delays between pages recommended
3. **Network latency**: Each page requires separate API call (~200-500ms)
4. **User experience**: Show progress for long operations (>3 pages)

## Example Usage

### Scenario 1: Small Result Set (Single Page)
```bash
/fabric:list-workspaces

# API returns:
{
  "value": [12 workspaces],
  "continuationToken": null
}

# Output:
✅ Found 12 workspaces

NAME                TYPE        CAPACITY
Dev Workspace       Workspace   cap-001
Test Workspace      Workspace   cap-001
...
```

### Scenario 2: Medium Result Set (Multi-Page, Fetch All)
```bash
/fabric:list-items my-workspace

# Pagination handler invoked

# Output:
📄 Fetching items...
📄 Fetched page 1 (100 items)...
📄 Fetched page 2 (100 items)...
📄 Fetched page 3 (100 items)...
📄 Fetched page 4 (73 items)...
✅ Found 373 items (4 pages)

NAME                       TYPE        ID
Sales Dashboard            Report      abc-123
Customer Analytics         Dashboard   def-456
ETL Pipeline              DataPipeline ghi-789
...
[Table continues with all 373 items]
```

### Scenario 3: Large Result Set (Streaming)
```bash
/fabric:list-items my-workspace --stream

# Output:
📄 Streaming results (page 1)...

Sales Dashboard (Report)
Customer Analytics (Dashboard)
ETL Pipeline (DataPipeline)
... [97 more items]

📄 Streaming results (page 2)...

Monthly Report (Report)
Quarterly Dashboard (Dashboard)
... [100 more items]

[Continues until all pages fetched]

✅ Streamed 847 items across 9 pages
```

### Scenario 4: Manual Pagination
```bash
/fabric:list-lakehouses my-workspace

# Output:
Lakehouse 1 - abc-123
Lakehouse 2 - def-456
...
Lakehouse 100 - xyz-789

📄 Page 1 complete. More results available.
Fetch next page? (y/n/a)

> y

Fetching next page...

Lakehouse 101 - aaa-111
Lakehouse 102 - bbb-222
...
```

## Testing Checklist
- [ ] No results (empty array) → Clear message
- [ ] Single page (<100 items) → Display all, no pagination message
- [ ] Multiple pages → Fetch all pages automatically
- [ ] Very large set (>1000 items) → Streaming or summary mode
- [ ] Malformed continuation token → Error handled gracefully
- [ ] Network error mid-pagination → Retry page, keep progress
- [ ] User cancellation (Ctrl+C) → Graceful stop, show partial results
- [ ] Export to file → All pages exported correctly
- [ ] Manual mode → Interactive prompts work correctly

## Related Skills
- `fabric-auth` - Provides access token for page requests
- `error-handler` - Handles errors during pagination

## API Documentation
- **Fabric API Pagination**: https://learn.microsoft.com/en-us/rest/api/fabric/articles/pagination
- **Continuation Tokens**: Pattern used across Microsoft APIs
