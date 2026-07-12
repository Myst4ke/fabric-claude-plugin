---
name: git-connect
description: Connect a workspace to a Git repository (Azure DevOps or GitHub)
---

# git-connect Skill

## Purpose
Connect a Microsoft Fabric workspace to a Git repository for version control of workspace items.

## Execution

**EXECUTE THIS IMMEDIATELY:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/git-connect/git_connect.py" "$@"
```

## Usage

```
git_connect.py <workspace> --provider {AzureDevOps,GitHub} --org ORG [--project PROJECT] --repo REPO --branch BRANCH [--directory DIR]
```

## Parameters
- `<workspace>` (required): Workspace **name or GUID** (names are resolved automatically)
- `--provider` (required): Git provider: `AzureDevOps` or `GitHub`
- `--org` (required): Organization name (Azure DevOps) or owner (GitHub)
- `--project` (required for AzureDevOps): Project name
- `--repo` (required): Repository name
- `--branch` (required): Branch name
- `--directory` (optional): Directory path in repo (default: `/`)

## Examples
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/git-connect/git_connect.py" "My Workspace" --provider AzureDevOps --org myorg --project myproject --repo myrepo --branch main
bash "${CLAUDE_PLUGIN_ROOT}/skills/_shared/py.sh" "${CLAUDE_PLUGIN_ROOT}/skills/git-connect/git_connect.py" a1b2c3d4-... --provider GitHub --org myowner --repo myrepo --branch main --directory /fabric
```

## Returns
- Success: Exit code 0, connection summary
- Error: Exit code 1-3, error message (1 if already connected or Admin role missing)

## Exit Codes
- 0: Success
- 1: Permanent error (usage error, not found, forbidden, already connected)
- 2: Retryable error (rate limit, server error)
- 3: Authentication error (run /fabric-plugin:\setup:login)
