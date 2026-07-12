# Microsoft Fabric Plugin for Claude Code

A Claude Code plugin for managing Microsoft Fabric directly from your terminal: workspaces, lakehouses, notebooks, data pipelines, warehouses, semantic models, KQL databases, Spark jobs, ML models and more — 112 skills and 5 specialized agents built on the Fabric REST API.

## Installation

```
/plugin marketplace add Myst4ke/fabric-claude-plugin
/plugin install fabric-plugin@fabric-toolbox
```

Then follow the setup guide: **[fabric-plugin/docs/AZURE_APP_SETUP.md](fabric-plugin/docs/AZURE_APP_SETUP.md)** (one-time Entra ID app registration, ~10 min), set `FABRIC_CLIENT_ID`, and sign in with `/fabric-plugin:setup:login`.

## Documentation

- **[Plugin README](fabric-plugin/README.md)** — features, prerequisites, quick start, full skill catalog
- **[Azure app setup](fabric-plugin/docs/AZURE_APP_SETUP.md)** — Entra ID app registration guide
- **[Troubleshooting](fabric-plugin/TROUBLESHOOTING.md)** — common errors and fixes
- **[Changelog](fabric-plugin/CHANGELOG.md)**

## License

MIT — see [LICENSE](LICENSE).
