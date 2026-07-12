#!/usr/bin/env python3
"""
Microsoft Fabric Authentication
Self-contained OAuth 2.0 delegated authentication with PKCE
"""

import json
import urllib.request
import urllib.parse
import urllib.error
import http.server
import socketserver
import webbrowser
import hashlib
import base64
import secrets
import os
import sys
import time
import threading
from datetime import datetime

# Configuration
CLIENT_ID = os.environ.get('FABRIC_CLIENT_ID')
REDIRECT_URI = "http://localhost:8080"
SCOPE = "https://api.fabric.microsoft.com/.default offline_access"
PORT = 8080


def _cache_dir():
    """Same per-user persistent cache dir as skills/_shared/token_manager.py
    (the two MUST agree or refreshed tokens land in a different file)."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '..', '_shared'))
    try:
        from token_manager import CACHE_DIR
        return CACHE_DIR
    except ImportError:
        cache = os.environ.get("FABRIC_PLUGIN_CACHE_DIR") or \
            os.path.join(os.path.expanduser("~"), ".fabric-plugin")
        try:
            os.makedirs(cache, mode=0o700, exist_ok=True)
            return cache
        except OSError:
            return os.getenv("TEMP", "/tmp")


CACHE_DIR = _cache_dir()

# AADSTS sub-codes proving the refresh token itself is dead (safe to delete).
# Same rule as token_manager: anything else must NOT destroy the refresh token.
TERMINAL_RT_CODES = ('AADSTS70008', 'AADSTS700082', 'AADSTS700084', 'AADSTS50173')

# Colors
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

# Global variable for callback server
auth_code_received = None

class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler for OAuth callback"""

    def do_GET(self):
        global auth_code_received

        # Parse URL and query parameters
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if 'code' in params:
            auth_code_received = params['code'][0]

            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Authentication Successful</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 500px;
        }
        .success-icon {
            font-size: 80px;
            margin-bottom: 20px;
            color: #4CAF50;
        }
        h1 { color: #4CAF50; margin: 0 0 10px 0; }
        p { color: #666; line-height: 1.6; }
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">&#x2713;</div>
        <h1>Authentication Successful!</h1>
        <p>You can close this window and return to the terminal.</p>
    </div>
</body>
</html>"""

            self.wfile.write(html.encode())

            # Save code to file
            code_file = os.path.join(CACHE_DIR, 'fabric-auth-code.txt')
            with open(code_file, 'w') as f:
                f.write(auth_code_received)

            print(f"Code saved to: {code_file}")
            print("\nAuthorization code received.")
            print("Shutting down server...")

            # Shutdown server
            threading.Thread(target=self.server.shutdown).start()
        else:
            # No code in URL
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"No authorization code received")

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


class FabricAuthenticator:
    """Microsoft Fabric OAuth 2.0 Authenticator"""

    def __init__(self, quiet=False, verbose=False, force=False, timeout=300):
        self.client_id = CLIENT_ID
        self.redirect_uri = REDIRECT_URI
        self.scope = SCOPE
        self.port = PORT
        self.quiet = quiet
        self.verbose = verbose
        self.force = force
        self.timeout = timeout

        # Cache locations
        self.cache_dir = CACHE_DIR
        self.access_token_file = os.path.join(self.cache_dir, 'fabric-plugin-token-delegated.json')
        self.refresh_token_file = os.path.join(self.cache_dir, 'fabric-plugin-refresh-token.json')

        # OAuth state
        self.code_verifier = None
        self.code_challenge = None
        self.authorization_code = None
        self.access_token = None
        self.refresh_token = None
        self.expires_in = None

    def log_info(self, message):
        """Log info message (unless quiet mode)"""
        if not self.quiet:
            print(message)

    def log_verbose(self, message):
        """Log verbose debug message"""
        if self.verbose:
            print(f"{Colors.BLUE}[DEBUG]:{Colors.NC} {message}")

    def generate_pkce(self):
        """Generate PKCE code verifier and challenge"""
        self.log_info(f"{Colors.YELLOW}Generating PKCE challenge...{Colors.NC}")

        # Generate code verifier (43-128 characters)
        self.code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')

        # Generate code challenge (SHA256 of verifier)
        challenge_bytes = hashlib.sha256(self.code_verifier.encode('utf-8')).digest()
        self.code_challenge = base64.urlsafe_b64encode(challenge_bytes).decode('utf-8').rstrip('=')

        self.log_info(f"{Colors.GREEN}[OK] PKCE challenge generated{Colors.NC}")
        self.log_verbose(f"Code verifier generated ({len(self.code_verifier)} chars)")
        self.log_verbose(f"Code challenge: {self.code_challenge[:20]}...")

    def build_auth_url(self):
        """Build authorization URL"""
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'code_challenge': self.code_challenge,
            'code_challenge_method': 'S256',
            'prompt': 'select_account'
        }

        base_url = "https://login.microsoftonline.com/organizations/oauth2/v2.0/authorize"
        auth_url = f"{base_url}?{urllib.parse.urlencode(params)}"

        self.log_verbose(f"Authorization URL: {auth_url}")

        return auth_url

    def open_browser(self, auth_url):
        """Open browser to authorization URL"""
        self.log_info(f"\n{Colors.YELLOW}Opening browser for Microsoft login...{Colors.NC}")
        self.log_info(f"\n{Colors.BLUE}Authorization URL:{Colors.NC}")
        self.log_info(auth_url)
        self.log_info("")

        try:
            webbrowser.open(auth_url)
        except Exception as e:
            self.log_verbose(f"Browser open failed: {e}")
            print("Please open the URL above manually in your browser")

    def start_callback_server(self):
        """Start local HTTP server and wait for OAuth callback"""
        global auth_code_received
        auth_code_received = None

        self.log_info(f"\n{Colors.YELLOW}Starting local server on port {self.port}...{Colors.NC}")
        self.log_info(f"{Colors.BLUE}Instructions:{Colors.NC}")
        self.log_info("1. Sign in with your Microsoft account in the browser")
        self.log_info("2. Accept the permission request")
        self.log_info("3. You'll be redirected back automatically\n")

        try:
            with socketserver.TCPServer(("", self.port), OAuthCallbackHandler) as httpd:
                self.log_info(f"{Colors.GREEN}[OK] Server started on port {self.port}{Colors.NC}")
                self.log_info(f"{Colors.YELLOW}[WAIT] Waiting for callback (timeout: {self.timeout}s)...{Colors.NC}")

                # Server will run until shutdown is called
                httpd.serve_forever()

                if auth_code_received:
                    self.log_info(f"{Colors.GREEN}[OK] Server completed successfully{Colors.NC}")
                    self.authorization_code = auth_code_received
                    return True
                else:
                    print(f"{Colors.RED}[ERROR] Server stopped but no code received{Colors.NC}")
                    return False

        except OSError as e:
            if e.errno == 98 or e.errno == 10048:  # Address already in use
                print(f"{Colors.RED}[ERROR] Port {self.port} is already in use{Colors.NC}")
                print(f"Please stop any application using port {self.port}")
                return False
            else:
                print(f"{Colors.RED}[ERROR] Server error: {e}{Colors.NC}")
                return False

    def exchange_code_for_tokens(self):
        """Exchange authorization code for access and refresh tokens"""
        self.log_info(f"\n{Colors.YELLOW}Exchanging authorization code for tokens...{Colors.NC}")

        self.log_verbose(f"Token endpoint: https://login.microsoftonline.com/organizations/oauth2/v2.0/token")
        self.log_verbose(f"Grant type: authorization_code")

        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'code': self.authorization_code,
            'redirect_uri': self.redirect_uri,
            'code_verifier': self.code_verifier
        }

        try:
            request = urllib.request.Request(
                "https://login.microsoftonline.com/organizations/oauth2/v2.0/token",
                data=urllib.parse.urlencode(data).encode(),
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

            with urllib.request.urlopen(request) as response:
                result = json.loads(response.read().decode())

            self.access_token = result.get('access_token')
            self.refresh_token = result.get('refresh_token')
            self.expires_in = result.get('expires_in')

            if self.verbose:
                print(json.dumps({
                    'has_access_token': self.access_token is not None,
                    'has_refresh_token': self.refresh_token is not None,
                    'expires_in': self.expires_in,
                    'token_type': result.get('token_type'),
                    'scope': result.get('scope')
                }, indent=2))

            if not self.access_token:
                print(f"{Colors.RED}[ERROR] Failed to get access token{Colors.NC}")
                return False

            self.log_info(f"{Colors.GREEN}[OK] Tokens received{Colors.NC}")
            self.log_info(f"  Access token acquired ({len(self.access_token)} chars)")
            self.log_info(f"  Expires in: {self.expires_in} seconds (~{self.expires_in // 60} minutes)")

            if self.refresh_token:
                self.log_info(f"  Refresh token acquired")
            else:
                self.log_verbose("WARNING: No refresh token received")

            self._cleanup_auth_code_file()
            return True

        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            try:
                error_data = json.loads(error_body)
                print(f"{Colors.RED}[ERROR] Token exchange failed{Colors.NC}")
                print(f"Error: {error_data.get('error')}")
                print(f"Description: {error_data.get('error_description')}")
            except:
                print(f"{Colors.RED}[ERROR] Token exchange failed: {e}{Colors.NC}")
            self._cleanup_auth_code_file()
            return False

    def _cleanup_auth_code_file(self):
        """Best-effort removal of the persisted OAuth authorization code."""
        try:
            code_file = os.path.join(CACHE_DIR, 'fabric-auth-code.txt')
            if os.path.exists(code_file):
                os.remove(code_file)
                self.log_verbose("Authorization code file removed")
        except OSError:
            pass

    def save_tokens(self):
        """Save tokens to cache files"""
        self.log_info(f"\n{Colors.YELLOW}Saving tokens...{Colors.NC}")

        self.log_verbose(f"Access token file: {self.access_token_file}")
        self.log_verbose(f"Refresh token file: {self.refresh_token_file}")

        # Save refresh token
        if self.refresh_token:
            refresh_data = {'refresh_token': self.refresh_token}
            with open(self.refresh_token_file, 'w') as f:
                json.dump(refresh_data, f)
            os.chmod(self.refresh_token_file, 0o600)
            self.log_info(f"{Colors.GREEN}[OK] Refresh token saved{Colors.NC}")
            self.log_verbose(f"Refresh token length: {len(self.refresh_token)} chars")
        else:
            self.log_info(f"{Colors.YELLOW}[WARN]  No refresh token received{Colors.NC}")

        # Save access token with expiration
        current_time = int(time.time())
        expires_at = current_time + self.expires_in - 60  # 60 second buffer

        self.log_verbose(f"Current time: {current_time}")
        self.log_verbose(f"Expires in: {self.expires_in}s")
        self.log_verbose(f"Expires at: {expires_at}")

        access_data = {
            'access_token': self.access_token,
            'expires_at': expires_at,
            'token_type': 'Bearer',
            'cached_at': current_time
        }

        with open(self.access_token_file, 'w') as f:
            json.dump(access_data, f, indent=2)
        os.chmod(self.access_token_file, 0o600)

        self.log_info(f"{Colors.GREEN}[OK] Access token cached{Colors.NC}")
        self.log_verbose(f"Valid for: {self.expires_in // 60} minutes")

    def test_api(self):
        """Test token with Fabric API"""
        self.log_info(f"\n{Colors.YELLOW}Testing token with Fabric API...{Colors.NC}")

        try:
            request = urllib.request.Request(
                "https://api.fabric.microsoft.com/v1/workspaces",
                headers={
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json'
                }
            )

            with urllib.request.urlopen(request) as response:
                data = json.loads(response.read().decode())

            self.log_info(f"{Colors.GREEN}[OK] Token works! Fabric API returned HTTP 200{Colors.NC}")

            if not self.quiet:
                workspaces = data.get('value', [])
                print(f"\n{Colors.BLUE}Your Fabric Workspaces:{Colors.NC}")
                print(f"  Total workspaces: {len(workspaces)}")

                if workspaces:
                    print()
                    for ws in workspaces:
                        print(f"  - {ws['displayName']} (ID: {ws['id']})")

            return True

        except urllib.error.HTTPError as e:
            print(f"{Colors.RED}[ERROR] Fabric API returned HTTP {e.code}{Colors.NC}")

            if not self.quiet:
                if e.code == 401:
                    print("  - Token is invalid")
                elif e.code == 403:
                    print("  - You need a Fabric license or trial")

            return False

    def check_existing_token(self):
        """Try to use existing refresh token"""
        if not os.path.exists(self.refresh_token_file):
            return False

        self.log_info(f"{Colors.YELLOW}Found existing refresh token. Trying to use it...{Colors.NC}")

        try:
            with open(self.refresh_token_file, 'r') as f:
                refresh_data = json.load(f)

            refresh_token = refresh_data.get('refresh_token')

            self.log_verbose(f"Refresh token file: {self.refresh_token_file}")
            self.log_verbose("Refresh token loaded from cache")

            # Request new access token
            data = {
                'grant_type': 'refresh_token',
                'client_id': self.client_id,
                'refresh_token': refresh_token,
                'scope': self.scope
            }

            request = urllib.request.Request(
                "https://login.microsoftonline.com/organizations/oauth2/v2.0/token",
                data=urllib.parse.urlencode(data).encode(),
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

            try:
                with urllib.request.urlopen(request) as response:
                    result = json.loads(response.read().decode())
            except urllib.error.HTTPError as e:
                self._handle_refresh_http_error(e)
                return False

            self.access_token = result.get('access_token')
            new_refresh = result.get('refresh_token')
            self.expires_in = result.get('expires_in')

            if self.verbose:
                print(json.dumps({
                    'has_access_token': self.access_token is not None,
                    'has_refresh_token': new_refresh is not None,
                    'expires_in': self.expires_in,
                    'refresh_token_changed': new_refresh != refresh_token
                }, indent=2))

            if self.access_token:
                self.log_info(f"{Colors.GREEN}[OK] Refreshed token successfully!{Colors.NC}")

                # Update refresh token if new one provided
                if new_refresh:
                    self.refresh_token = new_refresh
                    self.log_verbose("New refresh token received and will be saved")
                else:
                    self.refresh_token = refresh_token
                    self.log_verbose("Same refresh token, no update needed")

                # Save tokens
                self.save_tokens()

                # Test API
                if self.test_api():
                    if self.quiet:
                        print("[OK] Authentication successful")
                    else:
                        print(f"\n{Colors.GREEN}[OK] Authentication successful!{Colors.NC}")
                        print("No browser login needed (used refresh token).")
                    return True

            # Refresh did not produce a usable session. Keep the refresh
            # token file: only proven-terminal AADSTS errors may delete it
            # (handled in _handle_refresh_http_error).
            self.log_info(f"{Colors.YELLOW}[WARN]  Could not reuse the cached session{Colors.NC}")
            self.log_verbose("Possible causes:")
            self.log_verbose("  - Conditional Access policy")
            self.log_verbose("  - Token lifetime policy")
            self.log_verbose("  - Transient service issue")
            return False

        except Exception as e:
            self.log_verbose(f"Refresh token check failed: {e}")
            return False

    def _handle_refresh_http_error(self, error):
        """Parse the AADSTS error from a failed refresh. Delete the refresh
        token ONLY if it is provably dead (expired/revoked), never on
        scope/consent/CAE/transient failures (same rule as token_manager)."""
        body = ''
        try:
            body = error.read().decode('utf-8')
            err = json.loads(body)
        except Exception:
            err = {}

        error_code = err.get('error', '')
        description = err.get('error_description', body[:300])
        self.log_verbose(f"Token refresh failed: HTTP {error.code} "
                         f"error={error_code or 'unknown'}")

        if error_code == 'invalid_grant' and any(
                code in description for code in TERMINAL_RT_CODES):
            try:
                os.remove(self.refresh_token_file)
                self.log_info(f"{Colors.YELLOW}[WARN]  Refresh token expired or "
                              f"revoked - removed{Colors.NC}")
            except OSError:
                pass
            return

        # Non-terminal: keep the refresh token
        aadsts = next((tok for tok in description.split()
                       if tok.startswith('AADSTS')), None)
        hint = aadsts.rstrip(':,') if aadsts else f"HTTP {error.code}"
        self.log_info(f"{Colors.YELLOW}[WARN]  Token refresh failed ({hint}). "
                      f"Keeping cached refresh token.{Colors.NC}")

    def run(self):
        """Execute the authentication flow"""
        if not self.quiet:
            print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}")
            print(f"{Colors.BLUE}  Microsoft Fabric - Delegated Authentication{Colors.NC}")
            print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}\n")

        self.log_info("Configuration:")
        self.log_info(f"  Client ID: {self.client_id[:8]}...{self.client_id[-8:]}")
        self.log_info(f"  Redirect URI: {self.redirect_uri}")
        self.log_info(f"  Port: {self.port}\n")

        # Try refresh token first (unless force mode)
        if not self.force and self.check_existing_token():
            return 0

        if self.force:
            self.log_info(f"{Colors.BLUE}⚡ Force mode: Starting fresh login...{Colors.NC}\n")
        else:
            self.log_info(f"{Colors.BLUE}Starting interactive login flow...{Colors.NC}\n")

        # Generate PKCE
        self.generate_pkce()

        # Build auth URL and open browser
        auth_url = self.build_auth_url()
        self.open_browser(auth_url)

        # Start callback server
        if not self.start_callback_server():
            return 1

        # Exchange code for tokens
        if not self.exchange_code_for_tokens():
            return 1

        # Save tokens
        self.save_tokens()

        # Test API
        if not self.test_api():
            return 1

        # Success summary
        if not self.quiet:
            print(f"\n{Colors.BLUE}{'=' * 60}{Colors.NC}")
            print(f"{Colors.GREEN}[OK] Delegated Authentication Complete!{Colors.NC}")
            print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}\n")
            print("What was saved:")
            print(f"  1. Refresh token: {self.refresh_token_file}")
            print(f"  2. Access token: {self.access_token_file}\n")
            print("Next steps:")
            print("  - Your tokens are cached and ready to use")
            print(f"  - Access token valid for ~{self.expires_in // 60} minutes")
            print("  - Refresh token valid for months (auto-refresh)\n")
        else:
            print("[OK] Authentication complete")

        return 0


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Microsoft Fabric Authentication')
    parser.add_argument('--quiet', action='store_true', help='Minimal output')
    parser.add_argument('--verbose', action='store_true', help='Detailed debugging')
    parser.add_argument('--force', action='store_true', help='Force fresh login')
    parser.add_argument('--timeout', type=int, default=300, help='Callback timeout in seconds')

    args = parser.parse_args()

    if args.quiet and args.verbose:
        print("[ERROR] Cannot use --quiet and --verbose together")
        return 1

    if not CLIENT_ID:
        print(f"{Colors.RED}[ERROR] FABRIC_CLIENT_ID is not set.{Colors.NC}")
        print("Create an Entra ID app registration (see docs/AZURE_APP_SETUP.md "
              "in the plugin) and set the FABRIC_CLIENT_ID environment variable.")
        return 3

    authenticator = FabricAuthenticator(
        quiet=args.quiet,
        verbose=args.verbose,
        force=args.force,
        timeout=args.timeout
    )

    try:
        return authenticator.run()
    except KeyboardInterrupt:
        print("\n\nAuthentication cancelled by user")
        return 1
    except Exception as e:
        print(f"{Colors.RED}[ERROR] Unexpected error: {e}{Colors.NC}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
