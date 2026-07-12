# Fabric Plugin for Claude Code

**Version 0.5.0**

Comprehensive Microsoft Fabric integration providing 112 skills, 5 setup commands, and 5 specialized agents.

The interface is **skills + agents**: every Fabric operation is exposed as a skill (`fabric-plugin:<skill-name>`), invoked directly or orchestrated by the specialized agents. Slash commands only cover authentication/setup (`/fabric-plugin:setup:*`).

## Installation

From the `fabric-toolbox` marketplace:

```bash
/plugin marketplace add Myst4ke/fabric-claude-plugin
/plugin install fabric-plugin@fabric-toolbox
```

Local development alternative: clone the repository, then add it as a local marketplace:

```bash
git clone https://github.com/Myst4ke/fabric-claude-plugin.git
/plugin marketplace add <local-path-to-repo>
/plugin install fabric-plugin@fabric-toolbox
```

## Prerequisites

### Python

- **Python >= 3.9** available on PATH as `python3` or `python`. Skills use a bundled launcher shim (`skills/_shared/py.sh`) that tries `python3`, then `python`, then `py -3`.
- **Core skills are stdlib-only** — no pip packages required for the vast majority of operations.

### Optional dependencies

Only needed for specific skills (see `requirements-optional.txt`):

| Dependency | Needed by | Install |
|------------|-----------|---------|
| `pyodbc` + Microsoft ODBC Driver 17 or 18 for SQL Server | `lakehouse-sql-query`, `warehouse-query`, `warehouse-list-tables`, `table-query` | `pip install pyodbc` + driver below |
| `deltalake`, `pandas`, `pyarrow` | `table-read` | `pip install deltalake pandas pyarrow` |

ODBC driver installation:
- **Windows**: [ODBC Driver 18 MSI](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- **macOS**: `brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release && brew install msodbcsql18`
- **Linux**: apt/yum packages — see [Microsoft's Linux install guide](https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server)

### Microsoft Entra ID

- A **work or school account** is required (the authority is locked to `/organizations/` — personal Microsoft accounts will not work).
- There is **no bundled client ID**: you MUST create your own Entra app registration by following [`docs/AZURE_APP_SETUP.md`](docs/AZURE_APP_SETUP.md), then set the `FABRIC_CLIENT_ID` environment variable before logging in.

## Quick Start

```bash
# 0. One-time setup: create your Entra app registration (see docs/AZURE_APP_SETUP.md)
#    then set FABRIC_CLIENT_ID to your app's client ID
export FABRIC_CLIENT_ID="<your-app-client-id>"

# 1. Authenticate
/fabric-plugin:setup:login

# 2. List workspaces (skill)
fabric-plugin:workspace-list

# 3. Query data — arguments accept names or GUIDs
fabric-plugin:lakehouse-sql-query "My Workspace" "My Lakehouse" "SELECT TOP 10 * FROM dbo.mytable"
```

All skill scripts follow a unified CLI: positional `<workspace> [<item>] [extras]`, name-or-GUID resolution on every workspace/item argument, argparse flags with `-h`. Exit codes: 0 success, 1 permanent/usage, 2 retryable, 3 auth.

## Architecture

### Specialized Agents

Claude automatically delegates to the right agent based on your request:

| Agent | Domain | Trigger Examples |
|-------|--------|-----------------|
| **data-engineer** | Tables, lakehouses, SQL | "list tables", "query data", "load CSV" |
| **fabric-admin** | Workspaces, users | "list workspaces", "add user", "permissions" |
| **notebook-developer** | Notebooks | "run notebook", "cell results", "export ipynb" |
| **pipeline-engineer** | Pipelines | "run pipeline", "schedule daily", "pipeline logs" |
| **fabric-orchestrator** | Multi-step workflows | "run notebook then verify table" |

### Shared Infrastructure (`skills/_shared/`)

| Module | Purpose |
|--------|---------|
| `fabric_base.py` | `fabric_request` (retry 429/5xx + token refresh on 401), `fabric_list` (full pagination), `handle_http_error`, `connect_sql_endpoint` |
| `token_manager.py` | `get_token(audience)` multi-audience (fabric/sql/storage/graph/kusto), non-destructive refresh, atomic writes + lock, JWT audience validation |
| `cli_args.py` | `SkillCLI` — unified argument parsing (positional, name-or-GUID) |
| `fabric_resolver.py` | Workspace/item name resolution |
| `security_guard.py` | Warning-only security checks per environment |
| `audit_logger.py` | Operation audit trail |

### Security (`config/security.json`) — opt-in

**Optional.** With no `config/security.json` present, the plugin runs unrestricted.
Copy `config/security.json.example` to `config/security.json` and fill in your own
workspace GUIDs and policies to enable per-environment guardrails. Workspaces not
listed are *unmanaged* and allowed (a `[SECURITY]` warning is printed). Enforcement
currently applies to the SQL skills `warehouse-query` / `warehouse-list`.

Example environment policies you can define:

| Environment | Policy |
|-------------|--------|
| **PROD** | Read-only, confirmation required |
| **UAT** | Read + execute (notebooks/pipelines) |
| **DEV** | Full access |

## Skills Reference

### Authentication & Setup (5 slash commands)
- `/fabric-plugin:setup:login` - OAuth 2.0 authentication
- `/fabric-plugin:setup:logout` - Clear tokens
- `/fabric-plugin:setup:test-connection` - Verify connectivity
- `/fabric-plugin:setup:configure` - Plugin settings
- `/fabric-plugin:setup:help` - Usage help

### Workspace Operations (11 skills)
- `workspace-list` / `workspace-get`
- `workspace-create` / `workspace-update` / `workspace-delete`
- `workspace-user-list` / `workspace-user-add` / `workspace-user-remove` / `workspace-user-update-role`
- `workspace-assign-capacity` / `workspace-unassign-capacity`

### Lakehouse Operations (6 skills)
- **CRUD**: `lakehouse-list` / `lakehouse-get` / `lakehouse-create` / `lakehouse-update` / `lakehouse-delete`
- **SQL**: `lakehouse-sql-query` (T-SQL via SQL Analytics Endpoint, silent auth)

### Table Operations (11 skills)
- **CRUD**: `table-list` / `table-list-onelake` (schema-enabled lakehouses) / `table-get` / `table-create` / `table-delete` / `table-load`
- **Data**: `table-read` (Delta Lake direct read) / `table-query`
- **Schema**: `table-schema` / `table-properties` / `table-stats`

### File Operations (5 skills)
- `file-list` / `file-upload` / `file-download` / `file-delete`
- `onelake-list-files` (ADLS Gen2 compatible API)

### Notebook Operations (15 skills)
- **CRUD**: `notebook-list` / `notebook-get` / `notebook-create` / `notebook-update` / `notebook-delete` / `notebook-clone`
- **Execution**: `notebook-run` / `notebook-cancel` / `notebook-run-details` / `notebook-history` / `notebook-cell-results`
- **Definition**: `notebook-definition-get` / `notebook-definition-update` / `notebook-export` / `notebook-import`

### Pipeline Operations (15 skills)
- **CRUD**: `pipeline-list` / `pipeline-get` / `pipeline-create` / `pipeline-update` / `pipeline-delete` / `pipeline-clone`
- **Execution**: `pipeline-run` / `pipeline-cancel` / `pipeline-run-details` / `pipeline-history` / `pipeline-logs`
- **Diagnostics**: `pipeline-diagnose` (Diagnose a failed pipeline run down to the real notebook/Spark error)
- **Definition**: `pipeline-definition-get` / `pipeline-export` / `pipeline-import`

### Schedule Operations (5 skills)
- `schedule-list` / `schedule-create` / `schedule-update` / `schedule-delete` / `schedule-toggle`

### Semantic Model Operations (4 skills)
- `semantic-model-list` / `semantic-model-get`
- `semantic-model-refresh` / `semantic-model-refresh-history`

### Warehouse Operations (5 skills)
- **CRUD**: `warehouse-list` / `warehouse-get` / `warehouse-create`
- **Data**: `warehouse-query` / `warehouse-list-tables`

### Capacity Operations (3 skills)
- `capacity-list` / `capacity-get` / `capacity-metrics`

### Git Integration (5 skills)
- `git-connect` / `git-disconnect` - Connect/disconnect workspace to Git repo
- `git-status` - View connection and sync state
- `git-commit` - Commit workspace changes to Git
- `git-update` - Pull remote changes into workspace

### Environment Operations (5 skills)
- `environment-list` / `environment-get` / `environment-create`
- `environment-staging` - View pending library changes
- `environment-publish` - Publish staging (install/remove libraries)

### Spark Job Definitions (5 skills)
- `spark-job-list` / `spark-job-get` / `spark-job-create`
- `spark-job-run` / `spark-job-run-details`

### KQL / Real-Time Intelligence (5 skills)
- `kql-database-list` / `kql-database-get` / `kql-database-create`
- `kql-query` - Execute KQL queries (Kusto audience)
- `eventhouse-list`

### ML Models & Experiments (5 skills)
- `ml-model-list` / `ml-model-get` / `ml-model-create`
- `ml-experiment-list` / `ml-experiment-get`

### Core Infrastructure & Resolution (7 skills)
- `fabric-auth` / `fabric-login` / `email-to-guid` / `resolve-name`
- `error-handler` / `lro-handler` / `pagination-handler`

## Data Query Options

| Method | Use Case | Syntax |
|--------|----------|--------|
| **lakehouse-sql-query** | SQL with JOIN, GROUP BY, etc. | T-SQL via SQL Analytics Endpoint |
| **table-read** | Simple data extraction | Delta Lake via OneLake File API |
| **warehouse-query** | Warehouse SQL queries | T-SQL via Warehouse endpoint |

## Troubleshooting

### 401 Unauthorized
Token expired. All skills auto-refresh tokens via `get_token(audience)`.
If persists: `/fabric-plugin:setup:login`

### 429 Rate Limited
Skills retry automatically with exponential backoff via `fabric_request`.

### 403 Forbidden
Check workspace permissions. Need Contributor/Admin role for write operations.

### 404 Not Found
Verify workspace/item names or GUIDs. All skills accept names and resolve them automatically:
`notebook_run.py "My Workspace" "Sales Analysis"`

### Schema-enabled Lakehouse
If `table-list` fails, the lakehouse may use schemas. Use `table-list-onelake` or `lakehouse-sql-query`:
```sql
SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES
```

## Roadmap

All previously planned phases (Semantic Models, Warehouses, Git Integration, Environments, KQL/Eventhouses, ML Models, Spark Jobs, Capacity monitoring) are implemented. Remaining candidates: Reports/Dashboards, Dataflows, Mirroring, Data Activator, Connections & Gateways.

## Project Structure

```
fabric-plugin/
├── .claude-plugin/plugin.json    # Plugin manifest (5 agents)
├── agents/                       # 5 specialized agents
├── commands/
│   └── setup/                    # 5 setup commands (login, logout, configure, test-connection, help)
├── config/security.json.example  # Security policy template (opt-in)
├── docs/
│   └── AZURE_APP_SETUP.md        # Entra app registration guide
├── skills/                       # 112 skill implementations
│   ├── _shared/                  # Shared infrastructure
│   │   ├── fabric_base.py       # fabric_request / fabric_list / handle_http_error / connect_sql_endpoint
│   │   ├── token_manager.py     # get_token(audience), multi-audience, atomic refresh
│   │   ├── cli_args.py          # SkillCLI unified argument parsing
│   │   ├── fabric_resolver.py   # Name-to-GUID resolution
│   │   ├── security_guard.py    # Security checks
│   │   ├── audit_logger.py      # Audit trail
│   │   └── py.sh                # Python launcher shim (python3 → python → py -3)
│   ├── lakehouse-*/              # Lakehouse skills
│   ├── notebook-*/               # Notebook skills
│   ├── pipeline-*/               # Pipeline skills
│   ├── workspace-*/              # Workspace skills
│   └── ...                       # warehouse-*, semantic-model-*, kql-*, ml-*, git-*, environment-*, spark-job-*, capacity-*
├── requirements-optional.txt     # Optional dependencies (pyodbc, deltalake, pandas, pyarrow)
├── README.md                     # This file
└── CHANGELOG.md                  # Version history
```

## Author

**Myst4ke**

## License

MIT
