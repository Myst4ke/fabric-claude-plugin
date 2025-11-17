---
description: Display comprehensive help for Fabric plugin commands
argument-hint: [command-name]
---

# /fabric:help

## Purpose
Display comprehensive help documentation for the Microsoft Fabric plugin. Shows available commands, usage examples, and guides users to appropriate documentation based on their needs.

## Arguments
- `command-name`: Optional. Show detailed help for a specific command (e.g., `/fabric:help list-workspaces`)

## Prerequisites
None - this command is always available

## Instructions

### 1. Check for Specific Command Help
If user provides a command name argument, show detailed help for that command:

```bash
if [ -n "$1" ]; then
  command_name=$1

  # Display command-specific help
  case "$command_name" in
    "configure")
      echo "See: src/commands/setup/configure.md"
      # Show the description and usage from that command file
      ;;
    "test-connection")
      echo "See: src/commands/setup/test-connection.md"
      ;;
    "list-workspaces")
      echo "See: src/commands/workspace/list-workspaces.md"
      ;;
    *)
      echo "❌ Unknown command: $command_name"
      echo "Run /fabric:help to see all available commands"
      exit 1
      ;;
  esac
  exit 0
fi
```

### 2. Display Main Help Screen
Show comprehensive overview of the plugin:

```
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║    Microsoft Fabric Plugin for Claude Code                       ║
║    Version 0.1.0                                                  ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝

Manage Microsoft Fabric workspaces, items, and resources directly from
Claude Code. This plugin provides access to 197+ Fabric API operations.

═══════════════════════════════════════════════════════════════════

QUICK START

  1. Configure credentials:
     /fabric:configure

  2. Test your setup:
     /fabric:test-connection

  3. List your workspaces:
     /fabric:list-workspaces

═══════════════════════════════════════════════════════════════════

SETUP COMMANDS

  /fabric:configure [--validate]
    Set up Fabric API credentials interactively

  /fabric:test-connection [--verbose]
    Test API connectivity and authentication

  /fabric:help [command-name]
    Show this help or help for a specific command

═══════════════════════════════════════════════════════════════════

WORKSPACE COMMANDS

  /fabric:list-workspaces [--role <role>]
    List all accessible workspaces
    Options: --role Admin|Member|Contributor|Viewer

  /fabric:get-workspace <workspace-id>
    Get detailed information about a workspace

  /fabric:create-workspace <name> <capacity-id>
    Create a new workspace

  /fabric:delete-workspace <workspace-id>
    Delete a workspace (requires Admin role)

  /fabric:assign-capacity <workspace-id> <capacity-id>
    Assign a workspace to a capacity

═══════════════════════════════════════════════════════════════════

ITEM COMMANDS

  Coming in Phase 2-10:
  • Lakehouse operations
  • Notebook management
  • Data pipeline operations
  • Semantic model operations
  • Report management
  • And 180+ more operations...

═══════════════════════════════════════════════════════════════════

AUTHENTICATION

  This plugin uses OAuth 2.0 client credentials flow via Microsoft
  Entra ID (formerly Azure AD).

  Required environment variables:
    FABRIC_TENANT_ID      - Your Azure tenant ID
    FABRIC_CLIENT_ID      - Application (client) ID
    FABRIC_CLIENT_SECRET  - Client secret value

  Setup guide:
    Run /fabric:configure for step-by-step setup instructions

═══════════════════════════════════════════════════════════════════

COMMON OPERATIONS

  List workspaces:
    /fabric:list-workspaces

  Get workspace details:
    /fabric:get-workspace abc-123-def-456

  Create a lakehouse:
    /fabric:create-lakehouse <workspace-id> <name>

  Test connection:
    /fabric:test-connection --verbose

═══════════════════════════════════════════════════════════════════

TROUBLESHOOTING

  "Unauthorized" errors:
    • Run /fabric:configure to set up credentials
    • Check service principal is enabled in Fabric Admin Portal
    • Verify credentials with /fabric:test-connection

  "Forbidden" errors:
    • Add service principal to workspace (Admin/Member/Contributor role)
    • Check workspace-level permissions
    • Verify capacity permissions for capacity operations

  "Not Found" errors:
    • Verify resource ID is correct (must be GUID format)
    • Check you have access to the resource
    • Resource may have been deleted

  Rate limiting (429):
    • Plugin automatically retries with exponential backoff
    • Wait a few minutes if persistent
    • Reduce frequency of API calls

═══════════════════════════════════════════════════════════════════

RESOURCES

  Plugin repository:
    https://github.com/Myst4ke/fabric-claude-plugin

  Microsoft Fabric API documentation:
    https://learn.microsoft.com/en-us/rest/api/fabric/

  Report issues:
    https://github.com/Myst4ke/fabric-claude-plugin/issues

  Fabric service status:
    https://status.fabric.microsoft.com

═══════════════════════════════════════════════════════════════════

GETTING HELP

  For command-specific help:
    /fabric:help <command-name>

  Example:
    /fabric:help configure
    /fabric:help list-workspaces

  For questions or issues:
    • Check plugin documentation
    • Review command examples
    • Run commands with --help flag (where supported)
    • Report issues on GitHub

═══════════════════════════════════════════════════════════════════

PLUGIN INFORMATION

  Name:     fabric-plugin
  Version:  0.1.0
  Author:   Florian POSEZ
  License:  MIT
  Status:   Phase 1 (Foundation) - Active Development

  Currently implemented:
    ✓ 4 Core skills (auth, error handling, LRO, pagination)
    ✓ 3 Setup commands
    ✓ 2 Workspace commands
    ✓ 1 Agent (fabric-admin)

  Coming soon (Phase 2-10):
    ○ Complete workspace management
    ○ Data pipeline operations
    ○ Lakehouse & notebook operations
    ○ Power BI semantic models & reports
    ○ Advanced automation & CI/CD
    ○ 190+ additional operations

═══════════════════════════════════════════════════════════════════
```

### 3. Display Command-Specific Help
When user requests help for a specific command:

```
/fabric:help list-workspaces

═══════════════════════════════════════════════════════════════════

COMMAND: /fabric:list-workspaces

DESCRIPTION
  List all Microsoft Fabric workspaces accessible to the authenticated
  service principal.

USAGE
  /fabric:list-workspaces [--role <role>]

ARGUMENTS
  --role    Optional. Filter workspaces by your role
            Values: Admin, Member, Contributor, Viewer

EXAMPLES
  # List all workspaces
  /fabric:list-workspaces

  # List only workspaces where you're Admin
  /fabric:list-workspaces --role Admin

  # List workspaces where you're Contributor or higher
  /fabric:list-workspaces --role Contributor

OUTPUT
  Displays a formatted table with:
  • Workspace name
  • Workspace ID (GUID)
  • Type
  • Capacity assignment
  • Your role

NOTES
  • Automatically handles pagination for large result sets
  • Only shows workspaces you have access to
  • Empty list means no workspace access (not an error)

RELATED COMMANDS
  /fabric:get-workspace     Get detailed workspace information
  /fabric:create-workspace  Create a new workspace

═══════════════════════════════════════════════════════════════════
```

## Available Help Topics

### Configuration Help
When user asks about setup/configuration:
```
/fabric:help setup

SETUP GUIDE

To start using the Fabric plugin:

1. Create Service Principal (if needed)
   • Azure Portal → Azure Active Directory
   • App registrations → New registration
   • Copy Tenant ID and Client ID
   • Create client secret

2. Configure Plugin
   /fabric:configure

   This will prompt you for:
   • Tenant ID
   • Client ID
   • Client secret

3. Enable Service Principal in Fabric
   • Fabric Admin Portal → Tenant settings
   • Enable "Service principals can use Fabric APIs"
   • Add your SP to allowed list
   • Wait 15 minutes for propagation

4. Add SP to Workspaces
   • Open workspace → Manage access
   • Add service principal
   • Assign role (Admin/Member/Contributor)

5. Test Connection
   /fabric:test-connection

You're ready! Try: /fabric:list-workspaces
```

### Authentication Help
```
/fabric:help authentication

AUTHENTICATION GUIDE

The plugin uses OAuth 2.0 client credentials flow:

1. Plugin reads credentials from environment:
   • FABRIC_TENANT_ID
   • FABRIC_CLIENT_ID
   • FABRIC_CLIENT_SECRET

2. Acquires token from Microsoft Entra ID:
   POST https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token

3. Caches token (valid for 60 minutes)

4. Uses token in API requests:
   Authorization: Bearer {token}

Token is automatically refreshed when expired.

TROUBLESHOOTING

Unauthorized (401):
  • Check credentials are set
  • Run /fabric:test-connection
  • Verify service principal exists

Forbidden (403):
  • Enable SP in Fabric Admin Portal
  • Add SP to workspace
  • Grant appropriate role

Token expired:
  • Plugin auto-refreshes
  • Check system time is correct
  • Verify tenant ID is correct
```

### Error Help
```
/fabric:help errors

COMMON ERRORS & SOLUTIONS

401 Unauthorized
  Problem: Authentication failed
  Solution: Run /fabric:configure and /fabric:test-connection

403 Forbidden
  Problem: Insufficient permissions
  Solution: Add service principal to workspace with appropriate role

404 Not Found
  Problem: Resource doesn't exist or no access
  Solution: Verify resource ID and check permissions

429 Rate Limited
  Problem: Too many API requests
  Solution: Wait and retry (auto-handled by plugin)

500 Server Error
  Problem: Fabric service issue
  Solution: Retry in a few minutes, check service status

Network Errors
  Problem: Connection issues
  Solution: Check internet, firewall, proxy settings

For detailed error information, run commands with --verbose flag.
```

### API Reference Help
```
/fabric:help api

API REFERENCE

Base URL: https://api.fabric.microsoft.com/v1/

Authentication: OAuth 2.0 Bearer token

Rate Limits: ~100 items per page, API-enforced throttling

Pagination: continuationToken pattern

Long-running operations: 202 Accepted with polling

Common patterns:
  • List operations return paginated results
  • Create/Update operations may be async (LRO)
  • All operations require authentication
  • GUIDs used for resource identifiers

Official documentation:
  https://learn.microsoft.com/en-us/rest/api/fabric/

API specifications:
  https://github.com/microsoft/fabric-rest-api-specs
```

## Error Scenarios

### Unknown Command
```
/fabric:help unknown-command

❌ Unknown command: unknown-command

Available commands:
  • configure
  • test-connection
  • list-workspaces
  • get-workspace
  • help

Run /fabric:help to see all commands
```

### No Help Available
```
/fabric:help create-ml-model

ℹ️ Command not yet implemented

This command is planned for Phase 9 (ML & External Data).

Currently available commands:
  • Setup: configure, test-connection, help
  • Workspace: list-workspaces, get-workspace

Check back in future releases or see roadmap:
  https://github.com/Myst4ke/fabric-claude-plugin#roadmap
```

## Related Commands
- `/fabric:configure` - Set up credentials
- `/fabric:test-connection` - Test connection

## Testing Checklist
- [ ] No arguments → Display main help screen
- [ ] Valid command name → Show command-specific help
- [ ] Invalid command name → Error with available commands
- [ ] Help topics (setup, auth, errors) → Display topic help
- [ ] Formatted output → Clear and readable
- [ ] Examples included → Helpful and accurate
- [ ] Links work → URLs are correct
- [ ] Version displayed → Matches plugin.json
