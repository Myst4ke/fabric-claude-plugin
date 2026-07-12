---
description: Display comprehensive help for Fabric plugin commands
argument-hint: [command-name]
---

# /fabric-plugin:setup:help

## Purpose

Display comprehensive help information for the Microsoft Fabric plugin, including available commands, setup instructions, and troubleshooting guidance. Optionally show detailed help for a specific command.

## Arguments

- `command-name` (optional): Show detailed help for a specific command

## Prerequisites

None - this command works without any configuration

## Instructions

### 1. Input Validation

```bash
command_name="${1:-}"

# If specific command requested, validate it exists
if [ -n "$command_name" ]; then
  # Will show help for that command if available
  show_specific_help=true
else
  show_specific_help=false
fi
```

### 2. Display General Help

If no specific command requested, show overview:

```bash
if [ "$show_specific_help" = false ]; then
  cat <<'EOF'
════════════════════════════════════════════════════════
  Microsoft Fabric Plugin for Claude Code
════════════════════════════════════════════════════════

Comprehensive integration with Microsoft Fabric REST API

## 🚀 Quick Start

1. Authenticate with your Microsoft account:
   /fabric-plugin:setup:login

2. Test your connection:
   /fabric-plugin:setup:test-connection

3. List your workspaces:
   Ask Claude: "list my Fabric workspaces"
   (fabric-plugin:workspace-list skill)

## 📚 Available Commands & Skills

### Setup Commands
  /fabric-plugin:setup:configure          Configure API credentials
  /fabric-plugin:setup:login               Sign in with Microsoft account
  /fabric-plugin:setup:logout              Sign out and clear credentials
  /fabric-plugin:setup:test-connection     Test API connectivity
  /fabric-plugin:setup:help                Show this help message

All other operations are exposed as skills — just ask Claude in
natural language and the right skill is invoked automatically.

### Workspace Management (skills)
  fabric-plugin:workspace-list            List all workspaces
  fabric-plugin:workspace-get             Get workspace details
  fabric-plugin:workspace-create          Create new workspace
  fabric-plugin:workspace-delete          Delete workspace
  fabric-plugin:workspace-user-list       List workspace users
  fabric-plugin:workspace-user-add        Add user to workspace
  fabric-plugin:workspace-user-remove     Remove user from workspace

### Data Pipelines (skills)
  fabric-plugin:pipeline-list             List pipelines
  fabric-plugin:pipeline-run              Execute pipeline
  fabric-plugin:pipeline-history          View execution history

### Notebooks (skills)
  fabric-plugin:notebook-list             List notebooks
  fabric-plugin:notebook-run              Execute notebook

### Lakehouses (skills)
  fabric-plugin:lakehouse-list            List lakehouses
  fabric-plugin:lakehouse-sql-query       Run SQL query

## 🔑 Authentication

Two methods available:

1. **Microsoft Account (Recommended)**
   - Interactive browser login
   - Uses your existing Fabric permissions
   - Easy setup: /fabric-plugin:setup:login

2. **Service Principal**
   - For automation and CI/CD
   - Requires Azure AD app registration
   - Setup: /fabric-plugin:setup:configure

## 📖 Documentation

- Azure app setup guide: docs/AZURE_APP_SETUP.md
- Full docs: README.md and the docs/ directory

## 🆘 Troubleshooting

**Authentication failed?**
  → Run: /fabric-plugin:setup:login

**Permission denied?**
  → Check workspace role: ask Claude to list workspace users
    (fabric-plugin:workspace-user-list skill)

**Connection issues?**
  → Test connection: /fabric-plugin:setup:test-connection

**Need help with a command?**
  → /fabric-plugin:setup:help <command-name>

## 🔗 Resources

- Microsoft Fabric Docs: https://learn.microsoft.com/fabric/
- API Reference: https://learn.microsoft.com/rest/api/fabric/
- Claude Code Docs: https://code.claude.com/docs

════════════════════════════════════════════════════════

For detailed help on a specific command:
  /fabric-plugin:setup:help <command-name>

Example: /fabric-plugin:setup:help login

EOF
fi
```

### 3. Display Specific Command Help

If command name provided, show detailed help:

```bash
if [ "$show_specific_help" = true ]; then
  case "$command_name" in
    "login")
      cat <<'EOF'
Command: /fabric-plugin:setup:login

Sign in with your Microsoft account for Fabric API access.

Usage:
  /fabric-plugin:setup:login [--scopes <scopes>]

Description:
  Opens your browser to Microsoft login page. After signing in,
  tokens are cached and refreshed automatically for months.

Options:
  --scopes   Custom OAuth scopes (advanced)

Example:
  /fabric-plugin:setup:login

What happens:
  1. Browser opens to Microsoft login
  2. Sign in with your account
  3. Accept permissions
  4. Tokens cached automatically
  5. Ready to use Fabric commands!

After successful login, try asking Claude to list your
workspaces (fabric-plugin:workspace-list skill).
EOF
      ;;

    "logout")
      cat <<'EOF'
Command: /fabric-plugin:setup:logout

Sign out and clear all cached credentials.

Usage:
  /fabric-plugin:setup:logout [--all]

Description:
  Removes cached access tokens and refresh tokens.
  After logout, you'll need to authenticate again.

Options:
  --all      Clear all authentication data

Example:
  /fabric-plugin:setup:logout

What is cleared:
  - Access tokens
  - Refresh tokens
  - PKCE codes
  - All cached credentials

After logout, authenticate again with:
  /fabric-plugin:setup:login
EOF
      ;;

    "configure")
      cat <<'EOF'
Command: /fabric-plugin:setup:configure

Interactive setup for Fabric API credentials (service principal).

Usage:
  /fabric-plugin:setup:configure [--validate]

Description:
  Guides you through setting up Azure AD service principal
  credentials for API access. Use this for automation and CI/CD.

Options:
  --validate     Test existing credentials

What you'll need:
  - Azure AD Tenant ID
  - App Registration Client ID
  - Client Secret

For personal use, consider using:
  /fabric-plugin:setup:login (easier, no Azure AD setup)

Example:
  /fabric-plugin:setup:configure
EOF
      ;;

    "test-connection")
      cat <<'EOF'
Command: /fabric-plugin:setup:test-connection

Test Microsoft Fabric API connectivity and authentication.

Usage:
  /fabric-plugin:setup:test-connection [--verbose]

Description:
  Verifies your credentials work and API is accessible.
  Shows response time and available workspaces.

Options:
  --verbose      Show detailed connection information

Example:
  /fabric-plugin:setup:test-connection

What is tested:
  ✓ Credentials are configured
  ✓ Authentication succeeds
  ✓ API is accessible
  ✓ Permissions are working

Sample output:
  ✅ Authentication successful
  ✅ API accessible
  Response time: 234ms
  Available workspaces: 8
EOF
      ;;

    *)
      echo "Unknown command: $command_name"
      echo ""
      echo "Available commands:"
      echo "  login, logout, configure, test-connection, help"
      echo ""
      echo "Run '/fabric-plugin:setup:help' for general help"
      exit 1
      ;;
  esac
fi
```

## Error Scenarios

- **Unknown command name**: Show available commands
- **No errors possible**: This command is informational only

## Example Usage

```bash
# Show general help
/fabric-plugin:setup:help

# Show help for login command
/fabric-plugin:setup:help login

# Show help for test-connection
/fabric-plugin:setup:help test-connection
```

## Related Commands

- All other commands (this is the entry point for discovering them)
