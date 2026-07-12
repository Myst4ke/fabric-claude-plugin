# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Microsoft Fabric Claude Code Plugin** that provides comprehensive integration with the Microsoft Fabric REST API. The plugin enables management of Fabric workspaces, data pipelines, lakehouses, notebooks, semantic models, warehouses, KQL databases, Spark jobs, ML models, and other resources directly from Claude Code.

### Architecture

**Token-Efficient Design**: Direct integration with Claude Code's native features (skills, agents) rather than MCP servers.

**Two-Layer Approach**:
1. **Skills** (`fabric-plugin:<skill-name>`): Autonomous capabilities that execute Python scripts against the Fabric REST API. This is the primary interface for both agents and users.
2. **Agents**: Domain-specific AI assistants that orchestrate multiple skills for complex workflows.

Slash commands only cover authentication/setup (`/fabric-plugin:setup:*`). All other operations are exposed as skills — command wrappers would duplicate the skill namespace and waste context tokens.

**Current Implementation**:
- **Skills**: 112 skills organized by domain (see Skills section below)
- **Commands**: 5 setup commands (login, logout, configure, test-connection, help)
- **Agents**: 5 agents (fabric-admin, data-engineer, notebook-developer, pipeline-engineer, fabric-orchestrator)

## Critical Development Rules

### 1. Version Control Protocol

- **ALWAYS commit** changes after completing a logical unit of work
- Commit message format: `[Component] Brief description` (e.g., `[Skill:fabric-auth] Implement OAuth token caching`)
- Commit frequency: After each command/skill/agent implementation, not in batches
- Before starting new work: `git log --oneline -20`

### 2. Uncertainty Management

**ASK** the user for clarification when:
- API endpoint behavior is ambiguous
- Multiple implementation approaches exist
- Parameter formats are unclear
- Authentication method selection is needed

**NEVER** assume or guess critical implementation details. Document assumptions made in code comments.

## Technical Foundation

### Microsoft Fabric REST API

**Base URL**: `https://api.fabric.microsoft.com/v1/`

**Authentication**: OAuth 2.0 via Microsoft Entra ID
- Service Principal (client_credentials): Automated scripts, CI/CD
- Delegated Access (authorization_code): User-interactive scenarios

**Required Environment Variables**:
- `FABRIC_TENANT_ID`: Azure tenant GUID
- `FABRIC_CLIENT_ID`: App registration client ID — **required, there is no default client ID**. See `docs/AZURE_APP_SETUP.md` for how to create the app registration.
- `FABRIC_CLIENT_SECRET`: Client secret value (service principal auth only)

### Critical API Patterns

#### Long-Running Operations (LRO)
- Pattern: HTTP 202 Accepted response with `Location`, `x-ms-operation-id`, `Retry-After` headers
- Implementation: Poll `/operations/{operationId}` until status is "Succeeded" or "Failed"
- Operations: Item creation, notebook definition updates, data loading, table maintenance

#### Pagination
- Pattern: Response contains `value` array and `continuationToken`/`continuationUri`
- Implementation: handled by `fabric_list()` in `skills/_shared/fabric_base.py` (iterates all pages)
- Page size: ~100 items (not configurable)

#### Rate Limiting
- Detection: HTTP 429 Too Many Requests
- Handling: `fabric_request()` respects `Retry-After` and applies exponential backoff
- Max retries: 5

#### Error Handling Matrix
- 400 Bad Request: Validate input, show helpful message
- 401 Unauthorized: Re-authenticate, refresh token (automatic in `fabric_request()`)
- 403 Forbidden: Check workspace role/capacity permissions
- 404 Not Found: Verify ID, suggest list skills
- 429 Rate Limit: Implement backoff with Retry-After
- 500 Internal Server Error: Retry with backoff

**Fabric-Specific Errors**:
- `InsufficientPrivileges`: User lacks required workspace/capacity role
- `PrincipalTypeNotSupported`: Operation requires delegated auth (not service principal)
- `InvalidItemType`: Item type string is invalid or unsupported
- `FolderNotFound`: Specified folder doesn't exist in workspace

## Skill Conventions

All skill scripts follow a unified CLI convention:

### CLI
- **Positional arguments**: `<workspace> [<item>] [extras]`
- **Name or GUID everywhere**: every workspace/item argument accepts either a display name or a GUID; names are resolved automatically (fuzzy matching via `fabric_resolver.py`)
- **Optional flags** via argparse, with a working `-h`/`--help` on every script
- **Invocation** in SKILL.md files goes through a portable launcher shim (tries `python3`, then `python`, then `py -3`):

  ```
  bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/<dir>/<script>.py" <args...>
  ```

  Never invoke skill scripts with a bare `python3` in SKILL.md — not all platforms have that alias.

### Exit Codes
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Permanent error or usage error |
| 2 | Retryable error (rate limit, transient 5xx) |
| 3 | Authentication error (re-login needed) |

### Shared Infrastructure (`skills/_shared/`)
| Module | Provides |
|--------|----------|
| `py.sh` | Portable Python launcher shim (`python3` → `python` → `py -3`) |
| `fabric_base.py` | `fabric_request()` (retry on 429/5xx + token refresh on 401), `fabric_list()` (full pagination), `handle_http_error()`, `connect_sql_endpoint()` |
| `token_manager.py` | `get_token(audience)` multi-audience (fabric/sql/storage/graph/kusto), non-destructive refresh, atomic writes + lock, JWT audience validation |
| `cli_args.py` | `SkillCLI` — standard argument parsing (positional workspace/item, name-or-GUID resolution) |
| `fabric_resolver.py` | Workspace/item name-to-GUID resolution |

### Multi-Audience Silent Auth
- `get_token(audience)` returns the right token for each API: Fabric REST, SQL endpoints, OneLake storage, Microsoft Graph, Kusto
- SQL authentication (`lakehouse-sql-query`, `warehouse-query`) is silent — no interactive popup
- `kql-query` uses the Kusto audience
- Tokens are cached and refreshed transparently; refresh never destroys other audiences' tokens

## Plugin Structure

### Directory Layout

```
fabric-plugin/                        # Main plugin directory
├── .claude-plugin/
│   └── plugin.json                   # Plugin manifest (5 agents, commands dir, skills dir)
│
├── agents/                           # 5 specialized agents
│   ├── fabric-admin.md              # Workspaces, capacities, users, git, environments
│   ├── data-engineer.md             # Lakehouses, tables, files, SQL, warehouses, KQL, ML
│   ├── notebook-developer.md        # Notebooks, execution, definitions
│   ├── pipeline-engineer.md         # Data pipelines, orchestration, scheduling
│   └── fabric-orchestrator.md       # Multi-domain workflow coordination
│
├── commands/
│   └── setup/                       # 5 commands: login, logout, configure, test-connection, help
│
├── config/
│   └── security.json                # Per-environment security policies
│
├── docs/
│   └── AZURE_APP_SETUP.md           # App registration guide (FABRIC_CLIENT_ID)
│
└── skills/                           # 112 autonomous skills (organized by domain)
    ├── _shared/                     # Shared infrastructure (py.sh, fabric_base, token_manager, cli_args, ...)
    ├── workspace-*/                 # Workspace + user + capacity assignment
    ├── lakehouse-*/                 # Lakehouse CRUD + SQL
    ├── table-*/                     # Tables (REST + OneLake APIs)
    ├── file-*/  onelake-*/          # OneLake file operations
    ├── notebook-*/                  # Notebook CRUD + execution
    ├── pipeline-*/  schedule-*/     # Pipelines + diagnostics + scheduling
    ├── warehouse-*/                 # SQL warehouses
    ├── semantic-model-*/            # Power BI datasets
    ├── spark-job-*/                 # Spark job definitions
    ├── kql-*/  eventhouse-*/        # Real-Time Intelligence
    ├── ml-*/                        # ML models & experiments
    ├── git-*/                       # Workspace Git integration
    ├── environment-*/               # Spark/Python environments
    └── capacity-*/                  # Capacity monitoring
```

### plugin.json Critical Rules

- `repository` MUST be a string (URL), NOT an object
- `agents` MUST be an array of file paths, NOT a directory path
- All paths MUST be relative and start with `./`
- `commands` and `skills` CAN be directory paths (will scan for .md files)

## Component Specifications

### Slash Commands

Only the `setup` category exists (authentication and configuration). All other operations go through skills.

**Format**: Markdown with YAML frontmatter in `commands/setup/`.

### Agents

**Format**: Markdown with YAML frontmatter
**Tools**: Read, Write, Bash, Grep, Skill (fabric-orchestrator also has Task)

**Agent Roster** (5 implemented):
- `fabric-admin`: Workspaces, users, capacities, git integration, environments
- `data-engineer`: Lakehouses, tables, files, SQL, semantic models, warehouses, Spark, KQL, ML
- `notebook-developer`: Notebooks, execution, definitions, cloning
- `pipeline-engineer`: Data pipelines, orchestration, scheduling
- `fabric-orchestrator`: Multi-domain workflows, delegates to the other agents via the Task tool

### Skills

**Format**: Markdown with YAML frontmatter in dedicated directory (`SKILL.md`) plus a Python script following the Skill Conventions above.

**Skills by domain** (112 total):

**Core Infrastructure (4)**: `fabric-auth`, `error-handler`, `lro-handler`, `pagination-handler`

**Authentication & Resolution (3)**: `fabric-login`, `email-to-guid`, `resolve-name`

**Workspace Operations (11)**: `workspace-list`, `workspace-get`, `workspace-create`, `workspace-update`, `workspace-delete`, `workspace-assign-capacity`, `workspace-unassign-capacity`, `workspace-user-add`, `workspace-user-remove`, `workspace-user-list`, `workspace-user-update-role`

**Capacity Operations (3)**: `capacity-list`, `capacity-get`, `capacity-metrics`

**Lakehouse Operations (6)**: `lakehouse-list`, `lakehouse-get`, `lakehouse-create`, `lakehouse-update`, `lakehouse-delete`, `lakehouse-sql-query`

**Table Operations (11)**: `table-list`, `table-list-onelake`, `table-get`, `table-create`, `table-delete`, `table-load`, `table-read`, `table-query`, `table-schema`, `table-properties`, `table-stats`

**File Operations (5)**: `file-list`, `file-upload`, `file-download`, `file-delete`, `onelake-list-files`

**Pipeline Operations (15)**: `pipeline-list`, `pipeline-get`, `pipeline-create`, `pipeline-update`, `pipeline-delete`, `pipeline-clone`, `pipeline-definition-get`, `pipeline-export`, `pipeline-import`, `pipeline-run`, `pipeline-cancel`, `pipeline-history`, `pipeline-run-details`, `pipeline-logs`, `pipeline-diagnose`

**Schedule Operations (5)**: `schedule-list`, `schedule-create`, `schedule-update`, `schedule-delete`, `schedule-toggle`

**Notebook Operations (15)**: `notebook-list`, `notebook-get`, `notebook-create`, `notebook-update`, `notebook-delete`, `notebook-run`, `notebook-cancel`, `notebook-history`, `notebook-run-details`, `notebook-cell-results`, `notebook-definition-get`, `notebook-definition-update`, `notebook-export`, `notebook-import`, `notebook-clone`

**Warehouse Operations (5)**: `warehouse-list`, `warehouse-get`, `warehouse-create`, `warehouse-query`, `warehouse-list-tables`

**Semantic Models (4)**: `semantic-model-list`, `semantic-model-get`, `semantic-model-refresh`, `semantic-model-refresh-history`

**Spark Jobs (5)**: `spark-job-list`, `spark-job-get`, `spark-job-create`, `spark-job-run`, `spark-job-run-details`

**KQL / Real-Time Intelligence (5)**: `kql-database-list`, `kql-database-get`, `kql-database-create`, `kql-query`, `eventhouse-list`

**ML Models & Experiments (5)**: `ml-model-list`, `ml-model-get`, `ml-model-create`, `ml-experiment-list`, `ml-experiment-get`

**Git Integration (5)**: `git-connect`, `git-status`, `git-commit`, `git-update`, `git-disconnect`

**Environments (5)**: `environment-list`, `environment-get`, `environment-create`, `environment-staging`, `environment-publish`

## Implementation Patterns

### Authentication Flow

1. Skills call `get_token(audience)` from `skills/_shared/token_manager.py`
2. Token cache is validated (expiration with buffer, JWT audience check)
3. If invalid/missing, token is refreshed non-destructively (atomic write + lock)
4. Used in all API calls: `Authorization: Bearer {token}`

### LRO Implementation

1. Detect 202 response with `Location` header
2. Extract `x-ms-operation-id` and `Retry-After`
3. Poll operation status endpoint
4. Show progress updates (percentComplete)
5. Handle "Succeeded", "Failed", or timeout (10 minutes max)

### Pagination Implementation

Use `fabric_list()` from `fabric_base.py` — it collects all pages by following `continuationToken`/`continuationUri` until exhausted.

## Common Pitfalls

1. **Token Expiration**: handled by `token_manager.py` — do not hand-roll token caching in skills
2. **LRO Timeout**: Implement proper timeout handling (10 minutes max)
3. **Pagination**: Don't assume single page — use `fabric_list()`
4. **Rate Limiting**: handled by `fabric_request()` — do not bypass it with raw `requests` calls
5. **Workspace Roles**: Verify user has required role (Admin/Contributor) for operations
6. **Service Principal Limitations**: Some operations require delegated auth
7. **Item Types**: Use exact case-sensitive strings (e.g., "DataPipeline", "Notebook", "Lakehouse")
8. **Schema-enabled lakehouses**: `table-list` (REST API) fails on them — use `table-list-onelake` or `lakehouse-sql-query` (INFORMATION_SCHEMA)

## Development Workflow

1. **Follow the Skill Conventions** above (CLI, exit codes, launcher shim, `_shared` infrastructure)
2. **Implement Component**: model new skills on an existing one in the same domain
3. **Test Thoroughly**: run the script with `-h`, with names and with GUIDs
4. **Commit Changes**: Use `[Component] Description` format

## Future Development

Remaining API operations to implement (see `ROADMAP.md`):

- **Power BI**: Reports, Dashboards
- **Advanced Data**: Dataflows, Datamarts, Mirroring
- **Administration**: Deployment pipelines, Connections & Gateways, Monitoring/alerting
- **Other**: Data Activator / Reflex, OneLake shortcuts

**Note**: There is no need to reinstall the plugin after every change — it can be updated in the plugin management interface.
