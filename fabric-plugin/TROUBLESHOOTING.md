# Troubleshooting Guide — Fabric Plugin

Common errors when using the Fabric plugin skills (OneLake, SQL, authentication), with their causes and solutions.

Skill scripts are invoked through the Python shim:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/<dir>/<script>.py" [args...]
```

`${CLAUDE_PLUGIN_ROOT}` resolves to the installed plugin directory (typically `~/.claude/plugins/cache/fabric-toolbox/fabric-plugin/<version>/`).

---

## Error: "FriendlyNameSupportDisabled"

### Symptom
```
Error: FriendlyNameSupportDisabled
Message: WorkspaceId and ArtifactId should be either valid Guids or valid Names
```

### Cause
The OneLake File API received GUIDs instead of display names in the `abfss://` URI (or a mix of both).

### Status
Resolved — `table_read.py` automatically resolves display names via the Fabric REST API before building the OneLake URI.

### If the error persists

#### 1. Check the script version
```bash
grep -A 5 "get_workspace_info" "${CLAUDE_PLUGIN_ROOT}/skills/table-read/table_read.py"
```

You should see the name resolution logic:
```python
workspace_name = get_workspace_info(args.workspace_id, fabric_token)
lakehouse_info = get_lakehouse_info(args.workspace_id, args.lakehouse_id, fabric_token)
lakehouse_name = lakehouse_info['displayName']
```

#### 2. Restart Claude Code
Close Claude Code completely and restart it so the plugin cache reloads the current version of the skills.

#### 3. Check authentication
```bash
# Verify that token cache files exist and are recent
ls -lh "~/.fabric-plugin/fabric-plugin-token-delegated.json"
ls -lh "~/.fabric-plugin/fabric-plugin-token-storage.json"
```

If the tokens are expired:
```
/fabric-plugin:setup:login
```

#### 4. Test manually
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" \
  "${CLAUDE_PLUGIN_ROOT}/skills/table-read/table_read.py" \
  <workspace-id> <lakehouse-id> my_table --schema my_schema --limit 5
```

#### 5. Check the debug output
The script prints:
```
[INFO] Retrieving workspace and lakehouse information...
[INFO] Workspace: MyWorkspace
[INFO] Lakehouse: MyLakehouse
[DEBUG] URI: abfss://MyWorkspace@onelake.dfs.fabric.microsoft.com/MyLakehouse.Lakehouse/Tables/...
```

If the URI contains GUIDs instead of names, the cached script is outdated — update the plugin from the marketplace (or reinstall it) and restart Claude Code.

---

## Error: "UnsupportedOperationForSchemasEnabledLakehouse"

### Symptom
```
HTTP 400: UnsupportedOperationForSchemasEnabledLakehouse
The operation is not supported for Lakehouse with schemas enabled.
```

### Cause
The `table-list` skill uses the Fabric REST API, which does not support schema-enabled lakehouses.

### Solution
Use the `table-list-onelake` skill instead — it uses the OneLake Table API, which supports schemas:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" \
  "${CLAUDE_PLUGIN_ROOT}/skills/table-list-onelake/table_list_onelake.py" \
  <workspace-id> <lakehouse-id>
```

Alternatively, `lakehouse-sql-query` with `INFORMATION_SCHEMA.TABLES` also works on schema-enabled lakehouses.

---

## Error: Token Invalid Grant

### Symptom
```
AADSTS70000: Provided grant is invalid or malformed
```

### Cause
The wrong `client_id` was used for the refresh-token exchange, or `FABRIC_CLIENT_ID` is not set.

### Solution
`FABRIC_CLIENT_ID` is **required** — the plugin no longer ships a default fallback application ID. Set it to the client ID of your own Azure app registration:

```bash
export FABRIC_CLIENT_ID="<your-app-client-id>"
```

See `docs/AZURE_APP_SETUP.md` for how to create and configure the app registration (redirect URIs, API permissions, public client flow).

If the error persists after setting the variable, reset the authentication:
```
/fabric-plugin:setup:logout
/fabric-plugin:setup:login
```

---

## Error: UnicodeEncodeError (Windows)

### Symptom
```
UnicodeEncodeError: 'charmap' codec can't encode character
```

### Cause
The Windows console default code page cannot render some Unicode output.

### Status
Resolved — skill scripts output plain ASCII characters.

### If the error persists
Force UTF-8 output:
```powershell
# PowerShell
$env:PYTHONIOENCODING = "utf-8"
```
```bash
# Bash
export PYTHONIOENCODING=utf-8
```

---

## SQL Skills: ODBC Driver and Python Dependencies

The SQL skills (`lakehouse-sql-query`, `warehouse-query`, `warehouse-list-tables`, `table-query`) connect to Fabric SQL Analytics Endpoints via `pyodbc` and require the **Microsoft ODBC Driver 17 or 18 for SQL Server**.

### Error: "Can't open lib 'ODBC Driver 18 for SQL Server'" or "Data source name not found"

**Cause:** The Microsoft ODBC Driver for SQL Server is not installed. It is **not** pre-installed on Windows (only legacy drivers like "SQL Server" ship with the OS, and they cannot authenticate against Fabric).

**Solution — install the driver for your OS:**

- **Windows:** Download and install "Microsoft ODBC Driver 18 for SQL Server" (or 17) from the Microsoft download page: https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server
- **macOS:**
  ```bash
  brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
  brew install msodbcsql18
  ```
- **Linux (Debian/Ubuntu):** follow the Microsoft repository setup, then:
  ```bash
  sudo apt-get install msodbcsql18
  ```

Both driver versions 17 and 18 are supported — the skills detect whichever is available.

### Error: "ModuleNotFoundError: No module named 'pyodbc'"

```bash
pip install pyodbc
```

### Error: "ModuleNotFoundError: No module named 'deltalake'" (or 'pandas' / 'pyarrow')

The OneLake table skills (`table-read`, `table-list-onelake`) read Delta tables locally and need:

```bash
pip install deltalake pandas pyarrow
```

---

## Validation Tests

### Test 1: List tables
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" \
  "${CLAUDE_PLUGIN_ROOT}/skills/table-list-onelake/table_list_onelake.py" \
  <workspace-id> <lakehouse-id>
```

**Expected output:**
```
Total: N schema(s), M table(s)

[Schema: my_schema] (X tables)
  - my_table (DELTA)
  ...
```

### Test 2: Read a table
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" \
  "${CLAUDE_PLUGIN_ROOT}/skills/table-read/table_read.py" \
  <workspace-id> <lakehouse-id> my_table --schema my_schema --limit 5
```

**Expected output:**
```
====================================================================================================
  Table: my_table
====================================================================================================

Rows: 5 | Columns: 6
```

Workspace and lakehouse arguments accept either display names or GUIDs — names are resolved automatically.

---

## Support

If problems persist:

1. **Check the token cache:** `~/.fabric-plugin/fabric-plugin-*.json`
2. **Test connectivity:** `/fabric-plugin:setup:test-connection`
3. **Reset authentication:** `/fabric-plugin:setup:logout` then `/fabric-plugin:setup:login`
4. **Update the plugin:** make sure you are running the latest version from the marketplace, then restart Claude Code
5. **Open an issue:** https://github.com/Myst4ke/fabric-claude-plugin/issues
