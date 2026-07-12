# Changelog

## [0.5.0] - 2026-07-12

### Major: Portability & Public Release Preparation
- New portable Python launcher `skills/_shared/py.sh` (tries `python3`, then `python`, then `py -3`); all SKILL.md and agent invocations migrated to it — skills now work on Windows installs that lack a `python3` alias
- Token/config cache moved from the OS temp dir to a persistent per-user directory `~/.fabric-plugin` (override with `FABRIC_PLUGIN_CACHE_DIR`); tokens survive reboots and no longer collide between users on shared machines. Existing sessions must re-run `/fabric-plugin:setup:login` once
- **Breaking**: removed the built-in default client ID — `FABRIC_CLIENT_ID` is now required (see `docs/AZURE_APP_SETUP.md`)
- Removed the `jq` dependency from setup commands (replaced with Python stdlib one-liners)
- Added `requirements-optional.txt` (pyodbc; deltalake/pandas/pyarrow) — the core remains stdlib-only
- New `pipeline-diagnose` skill: drills into failed pipeline runs down to the real notebook/Spark error (112 skills total)

### Documentation
- README: new Installation and Prerequisites sections (marketplace install, Python/ODBC requirements, Entra ID app registration)
- TROUBLESHOOTING.md rewritten in English with machine-agnostic paths and placeholder IDs; new ODBC/pyodbc section
- New in-repo contributor guide `CLAUDE.md`
- Setup command docs fixed to the `/fabric-plugin:setup:*` namespace

### Bug Fixes
- Fixed ~100 malformed or stale command references printed by skill scripts (`/fabric-plugin:\<domain>:<cmd>` → real skill names)
- `resolve-name` and `table-query` SKILL.md invocations no longer depend on the current working directory
- `warehouse-list-tables` now explains how to install pyodbc instead of failing silently

## [0.4.0] - 2026-06-10

### Major: Unified Multi-Audience Authentication
- `token_manager.get_token(audience)` now serves all APIs: Fabric REST, SQL endpoints, OneLake storage, Microsoft Graph, Kusto
- Non-destructive refresh: refreshing one audience no longer invalidates tokens for other audiences
- Atomic token file writes with file locking (no more corrupted caches under concurrent skill runs)
- JWT audience validation before token use (prevents sending a token to the wrong API)
- Silent SQL authentication for `lakehouse-sql-query` and `warehouse-query` (removed the interactive login popup)
- Fixed `kql-query` to use the Kusto audience (was failing with Fabric-audience tokens)

### Major: Skill Migration to Unified CLI (100+ skills)
- All skills migrated to `SkillCLI` / `fabric_request` / `fabric_list` from `skills/_shared/`
- Unified CLI convention: positional `<workspace> [<item>] [extras]`, every workspace/item argument accepts a display name or a GUID (automatic resolution), argparse flags with working `-h`
- Standardized exit codes: 0 success, 1 permanent/usage, 2 retryable, 3 auth
- Real retry/backoff on 429/5xx and automatic token refresh on 401 via `fabric_request`
- Complete pagination on all list skills via `fabric_list` (no more truncated results)
- All SKILL.md files invoke scripts via `python3 "${CLAUDE_PLUGIN_ROOT}/skills/<dir>/<script>.py"`

### Removed: Command Wrappers (~106 commands)
- Deleted all per-operation slash command wrappers; only `setup/` commands remain (login, logout, configure, test-connection, help)
- Resolves the duplicated command/skill namespace: agents and users now go through `fabric-plugin:<skill-name>` skills
- Saves roughly 2k tokens per session of command-listing overhead

### Bug Fixes
- Repaired 3 skills with missing frontmatter that were invisible to the Skill tool: `warehouse-list`, `warehouse-query`, `onelake-list-files`

### Cleanup & Security
- Removed dead code (legacy `*_v2.py` scripts)
- Token excerpts no longer written to logs
- SQL identifier validation on warehouse/lakehouse query skills

## [0.3.0] - 2026-03-18

### New: Semantic Models (Power BI)
- **4 new skills**: list, get, refresh, refresh-history
- **4 new commands**: `semantic-model:list-models`, `get-model`, `refresh-model`, `refresh-history`
- Trigger dataset refresh after data ingestion
- View refresh history with duration and error details

### New: Warehouse Extended
- **3 new skills**: create, get, list-tables
- **3 new commands**: `warehouse:create-warehouse`, `get-warehouse`, `list-tables`
- Warehouse creation with LRO polling
- List tables/views via INFORMATION_SCHEMA (API + pyodbc fallback)

### New: Capacity Monitoring
- **3 new skills**: list, get, metrics
- **3 new commands**: `capacity:list-capacities`, `get-capacity`, `get-metrics`
- View capacity SKU, region, state, CU units
- List workspaces assigned to a capacity
- Workload states (requires Capacity Admin)

### Bug Fixes
- Fixed HTTP 400 on schema-enabled lakehouses: now detects and suggests SQL alternative
- Improved error messages with API response body details
- Added auto-refresh attempt on 401 before failing

### New: Git Integration
- **5 new skills**: connect, status, commit, update-from-git, disconnect
- **5 new commands**: `git:connect`, `git:status`, `git:commit`, `git:update-from-git`, `git:disconnect`
- Connect workspace to Azure DevOps or GitHub repos
- View sync status with changed items (workspace vs remote)
- Commit/pull with conflict resolution (PreferWorkspace/PreferRemote)
- LRO polling for async commit/update operations

### New: Environments (Spark/Python)
- **5 new skills**: list, get, create, staging, publish
- **5 new commands**: `environment:list-environments`, `get-environment`, `create-environment`, `get-staging`, `publish`
- View published libraries (PyPI, Conda, Wheel, JAR)
- View Spark compute configuration (runtime version, instance pool)
- Staging area management (pending unpublished changes)
- Publish with LRO polling (library installation can take minutes)

### New: Spark Job Definitions
- **5 new skills**: list, get, create, run, run-details
- **5 new commands**: `spark-job:list-jobs`, `get-job`, `create-job`, `run-job`, `run-details`
- Run Spark jobs via Items API (jobType=SparkJob)
- Run history with duration and failure reasons

### New: KQL Databases / Eventhouses (Real-Time Intelligence)
- **5 new skills**: kql-database-list, get, create, kql-query, eventhouse-list
- **5 new commands**: `kql:list-databases`, `get-database`, `create-database`, `query`, `list-eventhouses`
- Execute KQL queries via Kusto REST API
- Support for parent eventhouse association

### New: ML Models & Experiments (MLflow)
- **5 new skills**: ml-model-list, get, create, ml-experiment-list, get
- **5 new commands**: `ml:list-models`, `get-model`, `create-model`, `list-experiments`, `get-experiment`
- MLflow experiment tracking integration

### Agent Updates
- Updated data-engineer agent with Semantic Model and Warehouse skills
- Updated fabric-admin agent with Capacity Management and Git Integration skills
- Added new trigger phrases for automatic agent detection

## [0.2.0] - 2026-03-17

### Major: Skills Migration to fabric_base
- **Migrated 50 skills** from legacy `load_token()` to `fabric_base.get_token()` with auto-refresh
- Created `skills/_shared/fabric_base.py` - standard bootstrap module
- All skills now have automatic token refresh (eliminates 401 errors)
- Backward-compatible: falls back to legacy token loading if fabric_base unavailable

### Agent Architecture
- Added `fabric-orchestrator` agent for multi-step workflows
- Updated 4 existing agents with TRIGGER PHRASES for automatic detection
- Fixed `plugin.json` to include all 5 agents

### Documentation Consolidation
- Consolidated 15 docs into README.md + CHANGELOG.md + ROADMAP.md
- Removed obsolete implementation/deployment docs

### Cleanup
- Added `tmpclaude-*` to `.gitignore`
- Added automatic temp file cleanup to SessionEnd hook
- Removed empty skill directories

## [0.1.1] - 2026-03-16

### Reliability Improvements
- Created `token_manager.py` for automatic token refresh
- Created `retry_handler.py` with exponential backoff (429, 500, 503)
- Created `lakehouse-sql-query` skill (T-SQL via SQL Analytics Endpoint)
- Deprecated `table-query` skill (used non-existent API endpoint)
- Upgraded `table-list` and `warehouse-query` to v2 with retry logic

## [0.1.0] - 2026-03-12

### Initial Release
- 75 skills across 7 domains (workspace, lakehouse, notebook, pipeline, warehouse, OneLake, schedule)
- 85 commands
- 4 specialized agents (data-engineer, fabric-admin, notebook-developer, pipeline-engineer)
- OAuth 2.0 delegated authentication
- Security configuration (prod/uat/dev environments)
- Smart argument resolution (name-to-GUID fuzzy matching)
