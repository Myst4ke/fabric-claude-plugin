# Azure AD App Registration — Authentication Setup

The plugin authenticates with **OAuth 2.0 delegated flow + PKCE** (public client, no
client secret). Every skill acquires tokens silently from a single refresh token
obtained at login.

The plugin ships **no built-in client ID**: you must register your own Entra ID
application (a one-time, ~10 minute task) and point the plugin at it with the
`FABRIC_CLIENT_ID` environment variable. Until it is set, `/fabric-plugin:setup:login`
and every skill exit with a clear error referencing this guide.

---

## Register your own app

### 1. Register the application

Azure Portal → **Microsoft Entra ID** → **App registrations** → **New registration**.

- **Name**: e.g. `fabric-plugin-cli`
- **Supported account types**:
  - *Accounts in this organizational directory only* — if you only need your own tenant.
  - *Accounts in any organizational directory (multitenant)* — if you want to share the
    same app across several work/school tenants.
- **Redirect URI**: platform **Mobile and desktop applications**, value exactly:

  ```
  http://localhost:8080
  ```

  > The loopback port **8080** is hard-coded (`skills/fabric-login/authenticate.py`).
  > It must match exactly.

Click **Register**, then copy the **Application (client) ID**.

### 2. Make it a public client

App → **Authentication** → **Advanced settings** →
**Allow public client flows** = **Yes**.

(The plugin uses PKCE with no client secret, so it must be a public client.)

### 3. Add the delegated API permissions

The plugin requests tokens for several resources using the `.default` scope, so each
resource's delegated permission must be registered and consented. App → **API
permissions** → **Add a permission** → for each of the following, add a **Delegated**
permission:

| Resource (token audience) | Used by | Minimum delegated permission |
|---------------------------|---------|------------------------------|
| **Power BI Service** (`api.fabric.microsoft.com`) | Fabric REST API — all core skills | a delegated scope (e.g. `Workspace.Read.All` or broader per your need) |
| **Azure SQL Database** (`database.windows.net`) | `lakehouse-sql-query`, `warehouse-query`, `warehouse-list-tables` | `user_impersonation` |
| **Azure Storage** (`storage.azure.com`) | OneLake file & Delta reads (`table-read`, `file-*`) | `user_impersonation` |
| **Microsoft Graph** (`graph.microsoft.com`) | `email-to-guid` (email → object id) | `User.Read` |
| **Azure Data Explorer** (`kusto.kusto.windows.net`) | `kql-query`, KQL skills | `user_impersonation` |
| **offline_access** | silent refresh (all skills) | always requested |

Then click **Grant admin consent** (or have an admin do it).

> If your tenant does not pre-authorize the public client for
> `database.windows.net`, SQL skills automatically fall back to the Power BI scope
> (`token_manager.py` `fallback_scopes`) — no extra action needed.

### 4. Point the plugin at your app

Export the client id before using the plugin (add it to your shell profile to persist):

```bash
# bash / git-bash / WSL
export FABRIC_CLIENT_ID="<your-application-client-id>"
```

```powershell
# PowerShell
$env:FABRIC_CLIENT_ID = "<your-application-client-id>"
```

`FABRIC_CLIENT_ID` is read by both `skills/_shared/token_manager.py` and
`skills/fabric-login/authenticate.py`.

### 5. Log in

```bash
/fabric-plugin:setup:login
```

---

## Reference — app configuration the plugin expects

Derived from the code (`skills/fabric-login/authenticate.py`, `skills/_shared/token_manager.py`):

| Setting | Value |
|---------|-------|
| Client type | Public client (PKCE S256, no secret) |
| Redirect URI | `http://localhost:8080` (loopback, fixed port) |
| Authority | `https://login.microsoftonline.com/organizations/oauth2/v2.0/...` |
| Account types | Work/school (AAD) accounts — **not** personal Microsoft accounts |
| Client ID | none bundled — `FABRIC_CLIENT_ID` environment variable (required) |
| Requested scopes | `.default` per resource above + `offline_access` |

## Verifying an existing app (checklist)

To audit whether a given app works for the plugin:

- [ ] **Authentication → Allow public client flows** = Yes
- [ ] **Authentication → Mobile and desktop applications** contains `http://localhost:8080`
- [ ] **Authentication → Supported account types** matches your sharing scope
      (single vs multitenant)
- [ ] **API permissions** include the delegated permissions in the table above, with
      **admin consent granted**
