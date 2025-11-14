# Microsoft Fabric Plugin for Claude Code

A Claude Code plugin that enables seamless interaction with Microsoft Fabric workspaces, items, and resources directly from your development environment.

## Overview

This plugin provides custom slash commands, agents, and skills for managing Microsoft Fabric resources through the Fabric REST API. Automate workspace operations, create and manage items (lakehouses, warehouses, notebooks, semantic models), and perform data operations without leaving your Claude Code session.

## Features

- **Workspace Management**: List, create, update, and delete workspaces; manage capacity assignments
- **Item Operations**: Create and manage lakehouses, warehouses, notebooks, semantic models, and pipelines
- **Data Operations**: Load data to lakehouse tables, run table maintenance (V-Order, Z-Order, VACUUM)
- **Authentication**: Supports both service principal (client credentials) and delegated access flows
- **Smart Polling**: Automatic handling of long-running operations with progress updates
- **Error Handling**: Intelligent error messages with actionable solutions

## Prerequisites

- **Claude Code**: Installed and running
- **Microsoft Fabric Access**: Valid Azure/Entra ID tenant with Fabric resources
- **Authentication Credentials**: Service principal or user credentials with appropriate permissions

## Installation

### Method 1: From GitHub (Recommended)

```bash
# In Claude Code
/plugin marketplace add Myst4ke/fabric-claude-plugin
/plugin install fabric-plugin
/plugin enable fabric-plugin
```

### Method 2: Local Development

```bash
# Clone the repository
git clone https://github.com/Myst4ke/fabric-claude-plugin.git

# In Claude Code, load from local directory
/plugin load /path/to/fabric-claude-plugin/src
```

### Method 3: Configuration File

Add to your `~/.claude/config.json`:

```json
{
  "plugins": [
    "/path/to/fabric-claude-plugin/src"
  ]
}
```

## Configuration

### Environment Variables

Set these environment variables for authentication:

```bash
export FABRIC_TENANT_ID="your-tenant-id"
export FABRIC_CLIENT_ID="your-client-id"
export FABRIC_CLIENT_SECRET="your-client-secret"
```

### Azure Setup

1. **Register an Azure AD Application**:
   - Navigate to Azure Portal > Azure Active Directory > App registrations
   - Create new registration
   - Note the Application (client) ID and Directory (tenant) ID

2. **Create Client Secret**:
   - In your app registration, go to Certificates & secrets
   - Create new client secret and save the value

3. **Configure API Permissions**:
   - Add permissions under API permissions:
     - `Item.ReadWrite.All`
     - `Workspace.ReadWrite.All`
     - `Capacity.ReadWrite.All` (if managing capacities)

4. **Enable Service Principal in Fabric** (for service principal flow):
   - Navigate to Fabric Admin Portal > Tenant settings
   - Enable "Service principals can use Fabric APIs"
   - Add your service principal to workspace with appropriate role (Contributor/Admin)

## Quick Start

After installation and configuration:

```bash
# Test connection
/fabric:test-connection

# List workspaces
/fabric:list-workspaces

# Create a lakehouse
/fabric:create-lakehouse <workspace-id> <lakehouse-name>

# List items in a workspace
/fabric:list-items <workspace-id> --type Lakehouse
```

## Available Commands

### Configuration Commands
- `/fabric:configure` - Interactive setup for credentials
- `/fabric:test-connection` - Verify Fabric API connectivity

### Workspace Commands
- `/fabric:list-workspaces [--role <role>]` - List all accessible workspaces
- `/fabric:get-workspace <workspace-id>` - Get detailed workspace information
- `/fabric:create-workspace <name> <capacity-id>` - Create new workspace
- `/fabric:delete-workspace <workspace-id>` - Delete workspace
- `/fabric:assign-capacity <workspace-id> <capacity-id>` - Assign workspace to capacity

### Item Commands
- `/fabric:list-items <workspace-id> [--type <type>]` - List workspace items
- `/fabric:create-lakehouse <workspace-id> <name>` - Create lakehouse
- `/fabric:create-notebook <workspace-id> <name>` - Create notebook
- `/fabric:create-warehouse <workspace-id> <name>` - Create warehouse
- `/fabric:delete-item <workspace-id> <item-id>` - Delete item

### Data Commands
- `/fabric:load-table <workspace-id> <lakehouse-id> <table-name> <file-path>` - Load data to lakehouse table
- `/fabric:maintain-table <workspace-id> <lakehouse-id> <table-name> [--operation <op>]` - Run table maintenance

## Agents

### Fabric Manager Agent

The plugin includes an intelligent agent that automatically handles Fabric operations:

- Invoked automatically when you mention Fabric workspaces or items
- Manages authentication, token caching, and refresh
- Handles long-running operations with progress updates
- Translates API errors into user-friendly messages
- Implements smart retry logic with exponential backoff

## Architecture

```
src/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── commands/                 # Slash commands
│   ├── configure.md
│   ├── list-workspaces.md
│   └── ...
├── agents/                   # AI agents
│   └── fabric-manager.md
└── skills/                   # Autonomous skills
    └── fabric-auth/
        └── SKILL.md
```

## Supported Item Types

- **Data Engineering**: Environment, GraphQL, Lakehouse, Notebook, SparkJobDefinition
- **Data Science**: MLExperiment, MLModel, DataAgent
- **Data Factory**: CopyJob, Dataflow, DataPipeline, MirroredDatabase
- **Real-Time Intelligence**: Eventhouse, EventStream, KQLDatabase, KQLQueryset
- **Data Warehouse**: Warehouse, SQLEndpoint
- **Power BI**: Report, SemanticModel, Dashboard, Datamart

## API Reference

This plugin interacts with the Microsoft Fabric REST API:

- **Base URL**: `https://api.fabric.microsoft.com/v1/`
- **Authentication**: Microsoft Entra ID OAuth 2.0
- **Documentation**: [Microsoft Fabric REST API Docs](https://learn.microsoft.com/en-us/rest/api/fabric/)

## Development

### Project Structure

```bash
# Clone repository
git clone https://github.com/Myst4ke/fabric-claude-plugin.git
cd fabric-claude-plugin

# Plugin source is in src/
cd src
```

### Testing

```bash
# Load plugin locally in Claude Code
/plugin load /path/to/fabric-claude-plugin/src

# Test individual commands
/fabric:test-connection

# Check Claude Code logs for debugging
tail -f ~/.claude/logs/claude-code.log
```

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Troubleshooting

### Authentication Errors (401)

- Verify environment variables are set correctly
- Check that service principal is enabled in Fabric Admin Portal
- Ensure service principal has appropriate workspace role

### Permission Errors (403)

- Verify workspace permissions (need Contributor or Admin role)
- For capacity operations, check capacity contributor permissions
- Some operations require delegated flow instead of service principal

### Rate Limiting (429)

- Plugin automatically handles rate limiting with exponential backoff
- Reduce frequency of API calls if persistent
- Check Fabric service health status

### Connection Issues

Run `/fabric:test-connection` to diagnose connectivity problems.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Resources

- [Microsoft Fabric REST API Documentation](https://learn.microsoft.com/en-us/rest/api/fabric/)
- [Claude Code Documentation](https://docs.claude.com/claude-code)
- [Plugin Development Guide](https://docs.claude.com/claude-code/plugins)

## Support

- **Issues**: [GitHub Issues](https://github.com/Myst4ke/fabric-claude-plugin/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Myst4ke/fabric-claude-plugin/discussions)

## Acknowledgments

Built with [Claude Code](https://claude.com/claude-code) - An AI-powered coding assistant by Anthropic.

---

**Note**: This plugin is not affiliated with or endorsed by Microsoft. Microsoft Fabric is a trademark of Microsoft Corporation.
