#!/usr/bin/env python3
"""
Token Manager - Unified multi-audience token management for the Fabric plugin.

One refresh token (acquired at login with offline_access) is exchanged silently
for access tokens of any supported audience. Each audience has its own cache
file, validated on load (expiry AND JWT audience claim).

Public API:
    get_token(audience='fabric')   -> str   (generic, preferred)
    get_fabric_token()             -> str   (back-compat wrapper)
    get_sql_token()                -> str   (TDS endpoints: lakehouse/warehouse SQL)
    get_storage_token()            -> str   (OneLake / ADLS Gen2)
    get_graph_token()              -> str   (Microsoft Graph: email->GUID)
    get_kusto_token()              -> str   (KQL databases / eventhouses)

Reliability guarantees:
- The shared refresh token is ONLY deleted on proven-terminal AADSTS errors
  (expired/revoked), never on scope/consent/network failures.
- All cache writes are atomic (temp file + os.replace) under a file lock.
- A cached token whose JWT 'aud' claim does not match the requested audience
  is ignored (poisoned-cache protection).
"""

import base64
import json
import os
import sys
import tempfile
import time
import urllib.request
import urllib.parse
import urllib.error

def _default_cache_dir():
    """Per-user persistent cache dir. TEMP//tmp is shared across users on
    POSIX and wiped on reboot/tmpfiles-clean; ~/.fabric-plugin is private
    (0700) and survives, so a login lasts until the refresh token expires."""
    cache = os.environ.get("FABRIC_PLUGIN_CACHE_DIR") or \
        os.path.join(os.path.expanduser("~"), ".fabric-plugin")
    try:
        os.makedirs(cache, mode=0o700, exist_ok=True)
        return cache
    except OSError:
        return os.getenv("TEMP", "/tmp")


CACHE_DIR = _default_cache_dir()
REFRESH_TOKEN_FILE = f"{CACHE_DIR}/fabric-plugin-refresh-token.json"
LOCK_FILE = f"{CACHE_DIR}/fabric-plugin-token.lock"
CLIENT_ID = os.environ.get('FABRIC_CLIENT_ID')
TOKEN_URL = "https://login.microsoftonline.com/organizations/oauth2/v2.0/token"

# Supported audiences: scope requested at refresh + cache file + markers that
# the JWT 'aud' claim must contain (URL form or well-known app GUID).
AUDIENCES = {
    'fabric': {
        'scope': "https://api.fabric.microsoft.com/.default offline_access",
        'file': f"{CACHE_DIR}/fabric-plugin-token-delegated.json",
        'aud_markers': ['api.fabric.microsoft.com',
                        '00000009-0000-0000-c000-000000000000',
                        'analysis.windows.net/powerbi'],
    },
    'sql': {
        'scope': "https://database.windows.net/.default offline_access",
        # Fabric TDS endpoints also accept Power BI-audience tokens; some
        # tenants do not pre-authorize the public client for database.windows.net
        # (AADSTS65002), so fall back to the Power BI scope.
        'fallback_scopes': [
            "https://analysis.windows.net/powerbi/api/.default offline_access",
        ],
        'file': f"{CACHE_DIR}/fabric-plugin-token-sql.json",
        'aud_markers': ['database.windows.net',
                        '022907d3-0f1b-48f7-badc-1ba6abab6d66',
                        'analysis.windows.net/powerbi'],
    },
    'storage': {
        'scope': "https://storage.azure.com/.default offline_access",
        'file': f"{CACHE_DIR}/fabric-plugin-token-storage.json",
        'aud_markers': ['storage.azure.com',
                        'e406a681-f3d4-42a8-90b6-c2b029497af1'],
    },
    'graph': {
        'scope': "https://graph.microsoft.com/.default offline_access",
        'file': f"{CACHE_DIR}/fabric-plugin-token-graph.json",
        'aud_markers': ['graph.microsoft.com',
                        '00000003-0000-0000-c000-000000000000'],
    },
    'kusto': {
        'scope': "https://kusto.kusto.windows.net/.default offline_access",
        'file': f"{CACHE_DIR}/fabric-plugin-token-kusto.json",
        'aud_markers': ['kusto'],
    },
}

# Back-compat module constants (some skills import these directly)
FABRIC_TOKEN_FILE = AUDIENCES['fabric']['file']
SQL_TOKEN_FILE = AUDIENCES['sql']['file']
FABRIC_SCOPE = AUDIENCES['fabric']['scope']
SQL_SCOPE = AUDIENCES['sql']['scope']

# AADSTS sub-codes proving the refresh token itself is dead (safe to delete).
# Anything else (consent missing, scope invalid, CAE challenge, network, 5xx)
# must NOT destroy the shared refresh token.
# 70008/700082/700084: expired/inactive - 50173: revoked
# 70043: expired by Conditional Access sign-in frequency policy
TERMINAL_RT_CODES = ('AADSTS70008', 'AADSTS700082', 'AADSTS700084',
                     'AADSTS50173', 'AADSTS70043')


# =============================================================================
# Low-level helpers: JWT decode, atomic writes, file lock
# =============================================================================

def _decode_jwt_claims(token):
    """Decode JWT payload without verification. Returns dict or None."""
    try:
        payload = token.split('.')[1]
        payload += '=' * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload))
    except Exception:
        return None


def _audience_matches(token, audience):
    """Check the JWT 'aud' claim against expected markers for the audience."""
    claims = _decode_jwt_claims(token)
    if claims is None:
        return False  # opaque/corrupt token: don't trust the cache
    aud = str(claims.get('aud', '')).lower()
    return any(marker in aud for marker in AUDIENCES[audience]['aud_markers'])


def _atomic_write_json(path, data, secure=True):
    """Write JSON atomically (temp file in same dir + os.replace)."""
    directory = os.path.dirname(path) or '.'
    fd, tmp_path = tempfile.mkstemp(prefix='.fabric-tok-', dir=directory)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f, indent=2)
        if secure:
            try:
                os.chmod(tmp_path, 0o600)  # best-effort (no-op ACL on Windows)
            except OSError:
                pass
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


class _FileLock:
    """Cross-process lock around token refresh/persist. Best-effort:
    if locking is unavailable, proceeds without (atomic writes still
    protect against corruption; the lock only avoids duplicate refreshes)."""

    def __init__(self, path=LOCK_FILE, timeout=15):
        self.path = path
        self.timeout = timeout
        self._fh = None

    def __enter__(self):
        try:
            self._fh = open(self.path, 'a+')
            deadline = time.time() + self.timeout
            while True:
                try:
                    if os.name == 'nt':
                        import msvcrt
                        msvcrt.locking(self._fh.fileno(), msvcrt.LK_NBLCK, 1)
                    else:
                        import fcntl
                        fcntl.flock(self._fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    return self
                except OSError:
                    if time.time() > deadline:
                        return self  # give up waiting, proceed unlocked
                    time.sleep(0.2)
        except Exception:
            self._fh = None
            return self

    def __exit__(self, *exc):
        if self._fh:
            try:
                if os.name == 'nt':
                    import msvcrt
                    self._fh.seek(0)
                    msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(self._fh, fcntl.LOCK_UN)
            except Exception:
                pass
            self._fh.close()
        return False


# =============================================================================
# Token manager
# =============================================================================

class TokenManager:
    """Manages access tokens for one audience, refreshed from the shared
    refresh token."""

    def __init__(self, verbose=False, audience='fabric', scope=None, token_file=None):
        if audience not in AUDIENCES:
            raise ValueError(f"Unknown audience '{audience}'. "
                             f"Supported: {', '.join(AUDIENCES)}")
        self.verbose = verbose
        self.audience = audience
        # scope/token_file params kept for back-compat; audience config wins
        self.scope = scope or AUDIENCES[audience]['scope']
        self.token_file = token_file or AUDIENCES[audience]['file']
        self.access_token = None
        self.expires_at = None

    def log(self, message):
        if self.verbose:
            print(f"[TOKEN:{self.audience}] {message}")

    def get_token(self, force_refresh=False):
        """Get a valid access token for this audience, refreshing silently
        if needed. Exits with code 3 if a full re-login is required."""
        if not force_refresh and self._load_cached_token():
            if self._is_token_valid():
                self.log(f"Using cached token "
                         f"(valid {self.expires_at - int(time.time())}s)")
                return self.access_token
            self.log("Cached token expired, refreshing...")

        with _FileLock():
            # Another process may have refreshed while we waited for the lock
            if not force_refresh and self._load_cached_token() and self._is_token_valid():
                return self.access_token
            if self._refresh_token():
                return self.access_token

        print("[ERROR] Not authenticated or session expired.")
        print("Run: /fabric-plugin:setup:login")
        sys.exit(3)

    def _load_cached_token(self):
        if not os.path.exists(self.token_file):
            self.log("No cached token found")
            return False
        try:
            with open(self.token_file, 'r') as f:
                token_data = json.load(f)
            token = token_data.get('access_token')
            if not token:
                self.log("Invalid token data in cache")
                return False
            if not _audience_matches(token, self.audience):
                self.log("Cached token has WRONG audience - ignoring cache")
                return False
            self.access_token = token
            self.expires_at = token_data.get('expires_at', 0)
            return True
        except Exception as e:
            self.log(f"Failed to load cached token: {e}")
            return False

    def _is_token_valid(self):
        if not self.access_token or not self.expires_at:
            return False
        return self.expires_at > (int(time.time()) + 60)

    def _refresh_token(self):
        """Exchange the shared refresh token for an access token of this
        audience. NEVER deletes the refresh token except on proven-terminal
        AADSTS errors."""
        if not CLIENT_ID:
            print("[ERROR] FABRIC_CLIENT_ID is not set. Create an Entra ID app "
                  "registration (see docs/AZURE_APP_SETUP.md in the plugin) and "
                  "set the FABRIC_CLIENT_ID environment variable.", file=sys.stderr)
            sys.exit(3)
        if not os.path.exists(REFRESH_TOKEN_FILE):
            self.log("No refresh token found")
            return False

        try:
            with open(REFRESH_TOKEN_FILE, 'r') as f:
                refresh_data = json.load(f)
            refresh_token = refresh_data.get('refresh_token')
            if not refresh_token:
                self.log("Invalid refresh token data")
                return False
        except Exception as e:
            self.log(f"Failed to read refresh token: {e}")
            return False

        scopes = [self.scope] + AUDIENCES[self.audience].get('fallback_scopes', [])
        result = None
        for i, scope in enumerate(scopes):
            self.log(f"Requesting new access token (scope {i + 1}/{len(scopes)})...")
            data = urllib.parse.urlencode({
                'grant_type': 'refresh_token',
                'client_id': CLIENT_ID,
                'refresh_token': refresh_token,
                'scope': scope,
            }).encode('utf-8')

            try:
                request = urllib.request.Request(
                    TOKEN_URL, data=data,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
                response = urllib.request.urlopen(request, timeout=15)
                result = json.loads(response.read().decode('utf-8'))
                break
            except urllib.error.HTTPError as e:
                last_scope = (i == len(scopes) - 1)
                self._handle_refresh_http_error(e, quiet=not last_scope)
                if not os.path.exists(REFRESH_TOKEN_FILE):
                    return False  # refresh token was terminal-dead, stop
            except Exception as e:
                self.log(f"Token refresh error (network/transient): {e}")
                return False

        if result is None:
            return False

        self.access_token = result.get('access_token')
        if not self.access_token:
            self.log("Refresh response contained no access token")
            return False

        if not _audience_matches(self.access_token, self.audience):
            # Entra returned a token for another resource: do not cache it
            claims = _decode_jwt_claims(self.access_token) or {}
            self.log(f"Refreshed token has unexpected audience "
                     f"'{claims.get('aud')}' - not caching")
            return False

        expires_in = result.get('expires_in', 3600)
        self.expires_at = int(time.time()) + expires_in - 60
        self._save_tokens(result.get('refresh_token') or refresh_token)
        self.log(f"Token refreshed (valid {expires_in}s)")
        return True

    def _handle_refresh_http_error(self, error, quiet=False):
        """Parse the AADSTS error. Delete the shared refresh token ONLY if
        it is provably dead (expired/revoked), never on scope/consent/CAE/
        transient failures. With quiet=True (a fallback scope remains),
        warnings go to the verbose log only."""
        body = ''
        try:
            body = error.read().decode('utf-8')
            err = json.loads(body)
        except Exception:
            err = {}

        error_code = err.get('error', '')
        description = err.get('error_description', body[:300])
        self.log(f"Token refresh failed: HTTP {error.code} "
                 f"error={error_code or 'unknown'}")

        if error_code == 'invalid_grant' and any(
                code in description for code in TERMINAL_RT_CODES):
            try:
                os.remove(REFRESH_TOKEN_FILE)
                self.log("Refresh token expired/revoked - removed")
            except OSError:
                pass
            return

        # Non-terminal: keep the refresh token, surface a useful message
        aadsts = next((tok for tok in description.split()
                       if tok.startswith('AADSTS')), None)
        hint = aadsts.rstrip(':,') if aadsts else f"HTTP {error.code}"
        if quiet:
            self.log(f"Scope rejected ({hint}), trying fallback scope...")
            return
        print(f"[WARN] Could not get a token for audience "
              f"'{self.audience}' ({hint}).")
        if error_code in ('invalid_grant', 'interaction_required',
                          'consent_required'):
            print(f"[WARN] This scope may require consent in your tenant. "
                  f"The session itself remains valid for other operations.")

    def _save_tokens(self, refresh_token):
        """Persist access token (audience cache) + rotated refresh token,
        atomically."""
        try:
            _atomic_write_json(self.token_file, {
                'access_token': self.access_token,
                'expires_at': self.expires_at,
                'audience': self.audience,
                'token_type': 'Bearer',
                'cached_at': int(time.time()),
            })
            if refresh_token:
                current = None
                try:
                    with open(REFRESH_TOKEN_FILE, 'r') as f:
                        current = json.load(f).get('refresh_token')
                except Exception:
                    pass
                if refresh_token != current:
                    _atomic_write_json(REFRESH_TOKEN_FILE,
                                       {'refresh_token': refresh_token})
            self.log("Tokens saved to cache")
        except Exception as e:
            self.log(f"Failed to save tokens: {e}")


# =============================================================================
# Module-level API
# =============================================================================

_managers = {}


def get_token(audience='fabric', force_refresh=False, verbose=False):
    """
    Get a valid access token for the given audience, with silent refresh.

    Audiences: fabric (REST API), sql (TDS endpoints), storage (OneLake),
    graph (Microsoft Graph), kusto (KQL databases).

    Raises SystemExit(3) if re-login is required.
    """
    manager = _managers.get(audience)
    if manager is None:
        manager = _managers[audience] = TokenManager(
            verbose=verbose, audience=audience)
    manager.verbose = verbose or manager.verbose
    return manager.get_token(force_refresh=force_refresh)


def get_fabric_token(force_refresh=False, verbose=False):
    """Back-compat wrapper: token for the Fabric REST API."""
    return get_token('fabric', force_refresh=force_refresh, verbose=verbose)


def get_sql_token(force_refresh=False, verbose=False):
    """Token for SQL analytics endpoints (audience database.windows.net).
    Acquired silently - no browser/interactive prompt."""
    return get_token('sql', force_refresh=force_refresh, verbose=verbose)


def get_storage_token(force_refresh=False, verbose=False):
    """Token for OneLake / ADLS Gen2 (audience storage.azure.com)."""
    return get_token('storage', force_refresh=force_refresh, verbose=verbose)


def get_graph_token(force_refresh=False, verbose=False):
    """Token for Microsoft Graph (email -> GUID resolution)."""
    return get_token('graph', force_refresh=force_refresh, verbose=verbose)


def get_kusto_token(force_refresh=False, verbose=False):
    """Token for KQL databases / eventhouses (Kusto audience)."""
    return get_token('kusto', force_refresh=force_refresh, verbose=verbose)
