---
description: Sign in with Microsoft account for Fabric API access
argument-hint: [--scopes <scopes>]
---

# /fabric:login

## Purpose
Interactive command to authenticate with Microsoft Fabric API using your personal Microsoft account. This command opens a browser window for OAuth 2.0 authentication and stores tokens for future API calls. No Azure admin access required.

## Arguments
- `--scopes`: Optional. Comma-separated list of additional scopes to request beyond the minimal set

## Prerequisites
- Microsoft account (personal, work, or school)
- Access to at least one Fabric workspace
- Web browser
- Internet connectivity

## How It Works
1. Starts local HTTP server on port 8400
2. Opens browser to Microsoft sign-in page
3. You sign in and grant consent
4. Receives authorization code and exchanges it for tokens
5. Stores access token and refresh token securely
6. Closes local server

## Instructions

### 1. Display Welcome Message
```
🔐 Microsoft Fabric - User Authentication

This will open a browser window to sign in with your Microsoft account.

Authentication method: Delegated (user)
Port: 8400
Redirect URI: http://localhost:8400/callback

Press Enter to continue or Ctrl+C to cancel...
```

Wait for user to press Enter.

### 2. Check if Already Authenticated
```bash
TOKEN_CACHE="$HOME/.fabric/token_cache.json"

if [ -f "$TOKEN_CACHE" ]; then
  echo ""
  echo "⚠️ You are already signed in."
  echo ""
  echo "Current authentication expires: $(jq -r '.expires_at' "$TOKEN_CACHE" | xargs -I {} date -d @{})"
  echo ""
  echo "Do you want to sign in again? (y/n)"
  read -r response

  if [ "$response" != "y" ] && [ "$response" != "Y" ]; then
    echo "✅ Keeping existing authentication"
    exit 0
  fi

  echo "Clearing existing authentication..."
  rm -f "$TOKEN_CACHE"
fi
```

### 3. Set Up OAuth Configuration

**Default Client ID (Hybrid Approach):**
```bash
# Use Microsoft Azure CLI public client as default
# Users can override with FABRIC_CLIENT_ID environment variable
DEFAULT_CLIENT_ID="04b07795-8ddb-461a-bbee-02f9e1bf7b46"
CLIENT_ID="${FABRIC_CLIENT_ID:-$DEFAULT_CLIENT_ID}"

if [ "$CLIENT_ID" = "$DEFAULT_CLIENT_ID" ]; then
  echo "ℹ️  Using default public client"
  echo "   To use your own app, set: export FABRIC_CLIENT_ID=\"your-client-id\""
  echo ""
fi

# OAuth endpoints
AUTH_ENDPOINT="https://login.microsoftonline.com/organizations/oauth2/v2.0/authorize"
TOKEN_ENDPOINT="https://login.microsoftonline.com/organizations/oauth2/v2.0/token"
REDIRECT_URI="http://localhost:8400/callback"
```

**Minimal Scopes (as per user preference):**
```bash
# Start with minimal scopes
SCOPES="https://api.fabric.microsoft.com/Item.ReadWrite.All https://api.fabric.microsoft.com/Workspace.ReadWrite.All offline_access"

# Allow user to add additional scopes via --scopes argument
if [ -n "$additional_scopes" ]; then
  SCOPES="$SCOPES $additional_scopes"
fi

SCOPE_PARAM=$(echo "$SCOPES" | tr ' ' ',')
```

### 4. Generate PKCE Parameters

**Code Verifier (random 43-128 character string):**
```bash
CODE_VERIFIER=$(openssl rand -base64 64 | tr -d '\n' | tr '+/' '-_' | tr -d '=' | cut -c1-128)
```

**Code Challenge (SHA256 hash of verifier):**
```bash
CODE_CHALLENGE=$(echo -n "$CODE_VERIFIER" | openssl dgst -sha256 -binary | base64 | tr -d '\n' | tr '+/' '-_' | tr -d '=')
```

**State (CSRF protection):**
```bash
STATE=$(openssl rand -hex 16)
```

### 5. Start Local HTTP Server

Create a simple HTTP server to receive the authorization code:

```bash
# Create temporary directory for server
SERVER_DIR=$(mktemp -d)
RESPONSE_FILE="$SERVER_DIR/response.txt"

# Create server script
cat > "$SERVER_DIR/server.py" << 'EOF'
#!/usr/bin/env python3
import http.server
import socketserver
import urllib.parse
import sys
import os

PORT = 8400
RESPONSE_FILE = sys.argv[1]

class OAuthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/callback'):
            # Parse query parameters
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)

            if 'code' in params:
                code = params['code'][0]
                state = params.get('state', [''])[0]

                # Save code and state to file
                with open(RESPONSE_FILE, 'w') as f:
                    f.write(f"code={code}\n")
                    f.write(f"state={state}\n")

                # Send success response to browser
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                html = """
                <html>
                <head><title>Authentication Successful</title></head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: #28a745;">✅ Authentication Successful!</h1>
                    <p>You have successfully signed in to Microsoft Fabric.</p>
                    <p>You can close this window and return to the terminal.</p>
                </body>
                </html>
                """
                self.wfile.write(html.encode())

                # Shutdown server after successful response
                os._exit(0)

            elif 'error' in params:
                error = params['error'][0]
                error_desc = params.get('error_description', ['Unknown error'])[0]

                # Send error response
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                html = f"""
                <html>
                <head><title>Authentication Failed</title></head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: #dc3545;">❌ Authentication Failed</h1>
                    <p><strong>Error:</strong> {error}</p>
                    <p>{error_desc}</p>
                    <p>Please close this window and try again.</p>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
                os._exit(1)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress server logs
        pass

with socketserver.TCPServer(("", PORT), OAuthHandler) as httpd:
    print(f"Server listening on port {PORT}")
    httpd.serve_forever()
EOF

chmod +x "$SERVER_DIR/server.py"

# Start server in background
python3 "$SERVER_DIR/server.py" "$RESPONSE_FILE" > /dev/null 2>&1 &
SERVER_PID=$!

echo "🌐 Local server started on port 8400"
```

### 6. Build Authorization URL and Open Browser

```bash
# Build authorization URL with PKCE
AUTH_URL="${AUTH_ENDPOINT}?\
client_id=${CLIENT_ID}\
&response_type=code\
&redirect_uri=${REDIRECT_URI}\
&scope=${SCOPE_PARAM}\
&state=${STATE}\
&code_challenge=${CODE_CHALLENGE}\
&code_challenge_method=S256\
&prompt=select_account"

echo ""
echo "🌐 Opening browser for authentication..."
echo ""

# Open browser (cross-platform)
if command -v xdg-open > /dev/null; then
    xdg-open "$AUTH_URL" 2>/dev/null
elif command -v open > /dev/null; then
    open "$AUTH_URL"
elif command -v start > /dev/null; then
    start "$AUTH_URL"
else
    echo "Please open this URL in your browser:"
    echo "$AUTH_URL"
fi

echo "Waiting for authentication..."
echo "(This may take up to 2 minutes)"
```

### 7. Wait for Authorization Code

```bash
# Wait for response file to be created (with timeout)
TIMEOUT=120
ELAPSED=0

while [ ! -f "$RESPONSE_FILE" ] && [ $ELAPSED -lt $TIMEOUT ]; do
    sleep 1
    ELAPSED=$((ELAPSED + 1))

    # Show progress every 10 seconds
    if [ $((ELAPSED % 10)) -eq 0 ]; then
        echo "Still waiting... (${ELAPSED}s elapsed)"
    fi
done

# Check if we timed out
if [ ! -f "$RESPONSE_FILE" ]; then
    echo ""
    echo "❌ Authentication timed out after ${TIMEOUT} seconds"
    echo ""
    echo "Possible causes:"
    echo "  • Browser didn't open automatically"
    echo "  • You canceled the authentication"
    echo "  • Network connectivity issues"
    echo ""
    echo "Please try again: /fabric:login"

    # Cleanup
    kill $SERVER_PID 2>/dev/null
    rm -rf "$SERVER_DIR"
    exit 1
fi

# Read authorization code and state
AUTH_CODE=$(grep "code=" "$RESPONSE_FILE" | cut -d'=' -f2)
RECEIVED_STATE=$(grep "state=" "$RESPONSE_FILE" | cut -d'=' -f2)

# Verify state matches (CSRF protection)
if [ "$RECEIVED_STATE" != "$STATE" ]; then
    echo "❌ Security validation failed (state mismatch)"
    kill $SERVER_PID 2>/dev/null
    rm -rf "$SERVER_DIR"
    exit 1
fi

echo "✅ Authorization code received"
```

### 8. Exchange Authorization Code for Tokens

```bash
echo ""
echo "🔑 Exchanging authorization code for tokens..."

# Make token request
TOKEN_RESPONSE=$(curl -s -X POST "$TOKEN_ENDPOINT" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "client_id=${CLIENT_ID}" \
  -d "code=${AUTH_CODE}" \
  -d "redirect_uri=${REDIRECT_URI}" \
  -d "code_verifier=${CODE_VERIFIER}")

# Check for errors
if echo "$TOKEN_RESPONSE" | jq -e '.error' > /dev/null; then
    ERROR=$(echo "$TOKEN_RESPONSE" | jq -r '.error')
    ERROR_DESC=$(echo "$TOKEN_RESPONSE" | jq -r '.error_description')

    echo "❌ Token exchange failed"
    echo ""
    echo "Error: $ERROR"
    echo "Description: $ERROR_DESC"
    echo ""

    # Cleanup
    kill $SERVER_PID 2>/dev/null
    rm -rf "$SERVER_DIR"
    exit 1
fi

# Extract tokens
ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token')
REFRESH_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.refresh_token')
EXPIRES_IN=$(echo "$TOKEN_RESPONSE" | jq -r '.expires_in')
SCOPE=$(echo "$TOKEN_RESPONSE" | jq -r '.scope')

echo "✅ Tokens acquired successfully"
```

### 9. Store Tokens Securely

```bash
echo ""
echo "💾 Storing tokens..."

# Create ~/.fabric directory if it doesn't exist
mkdir -p "$HOME/.fabric"

# Calculate expiration timestamp
CURRENT_TIME=$(date +%s)
EXPIRES_AT=$((CURRENT_TIME + EXPIRES_IN - 60))

# Create token cache
cat > "$HOME/.fabric/token_cache.json" << EOF
{
  "auth_type": "delegated",
  "access_token": "$ACCESS_TOKEN",
  "refresh_token": "$REFRESH_TOKEN",
  "expires_at": $EXPIRES_AT,
  "token_type": "Bearer",
  "scope": "$SCOPE",
  "created_at": $CURRENT_TIME
}
EOF

# Set secure file permissions (owner read/write only)
chmod 600 "$HOME/.fabric/token_cache.json"

echo "✅ Tokens stored securely at ~/.fabric/token_cache.json"
```

### 10. Set Environment Variable

```bash
# Set auth type for current session
export FABRIC_AUTH_TYPE="delegated"

echo "✅ FABRIC_AUTH_TYPE set to 'delegated'"
```

### 11. Cleanup and Display Success

```bash
# Cleanup
kill $SERVER_PID 2>/dev/null
rm -rf "$SERVER_DIR"

# Display success message
echo ""
echo "✅ Authentication Complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Signed in successfully with Microsoft account"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Authentication details:"
echo "  • Type: Delegated (user)"
echo "  • Token expires: $(date -d @$EXPIRES_AT '+%Y-%m-%d %H:%M:%S')"
echo "  • Scopes: $SCOPE"
echo ""
echo "Next steps:"
echo "  1. List your workspaces: /fabric\\:workspace:list-workspaces"
echo "  2. View your permissions: Limited to your actual Fabric access"
echo "  3. Sign out when done: /fabric\\:logout"
echo ""
echo "Important notes:"
echo "  • Your access is limited to workspaces you have permission to"
echo "  • Some admin operations may require higher privileges"
echo "  • Token will auto-refresh for up to 90 days"
echo "  • After 90 days, run /fabric\\:login again"
echo ""
```

## Error Scenarios

### Scenario 1: Port 8400 Already in Use
```
❌ Failed to start local server

Port 8400 is already in use.

Actions:
  • Close other applications using port 8400
  • Check: netstat -an | grep 8400
  • Or: lsof -i :8400

Try again after freeing the port.
```

### Scenario 2: Browser Doesn't Open
```
🌐 Opening browser for authentication...

⚠️  If browser didn't open automatically, visit this URL:

https://login.microsoftonline.com/organizations/oauth2/v2.0/authorize?...

Waiting for authentication...
```

### Scenario 3: User Cancels Authentication
```
❌ Authentication canceled

You canceled the authentication flow in the browser.

To try again: /fabric:login
```

### Scenario 4: Permission Denied
```
❌ Consent required

The application requires additional permissions.

Please:
  1. Retry authentication: /fabric:login
  2. When prompted, check "Consent on behalf of your organization"
  3. Or contact your admin to pre-approve the application
```

### Scenario 5: Network Error
```
❌ Network error during authentication

Could not connect to Microsoft authentication servers.

Please check:
  • Internet connectivity
  • Firewall/proxy settings
  • Corporate network restrictions

Error details: {error_message}
```

## Testing Checklist
- [ ] Opens browser automatically on Windows/Mac/Linux
- [ ] Handles user consent and successful authentication
- [ ] Stores tokens with correct permissions (0600)
- [ ] Shows clear error if port 8400 is in use
- [ ] Handles authentication timeout (2 minutes)
- [ ] Detects existing authentication and prompts before overwriting
- [ ] Works with default public client ID
- [ ] Works with custom FABRIC_CLIENT_ID
- [ ] State parameter validated correctly (CSRF protection)
- [ ] Success message shows token expiration time
- [ ] FABRIC_AUTH_TYPE set correctly

## Related Commands
- `/fabric:logout` - Sign out and clear tokens
- `/fabric:configure` - Set up service principal authentication
- `/fabric:test-connection` - Test your authentication

## Example Usage

### First Time Sign In
```
$ /fabric:login

🔐 Microsoft Fabric - User Authentication

This will open a browser window to sign in with your Microsoft account.

Authentication method: Delegated (user)
Port: 8400
Redirect URI: http://localhost:8400/callback

Press Enter to continue or Ctrl+C to cancel...

ℹ️  Using default public client
   To use your own app, set: export FABRIC_CLIENT_ID="your-client-id"

🌐 Local server started on port 8400

🌐 Opening browser for authentication...

Waiting for authentication...
Still waiting... (10s elapsed)
✅ Authorization code received

🔑 Exchanging authorization code for tokens...
✅ Tokens acquired successfully

💾 Storing tokens...
✅ Tokens stored securely at ~/.fabric/token_cache.json
✅ FABRIC_AUTH_TYPE set to 'delegated'

✅ Authentication Complete!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Signed in successfully with Microsoft account
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Authentication details:
  • Type: Delegated (user)
  • Token expires: 2025-01-18 15:30:00
  • Scopes: https://api.fabric.microsoft.com/Item.ReadWrite.All...

Next steps:
  1. List your workspaces: /fabric\:workspace:list-workspaces
  2. View your permissions: Limited to your actual Fabric access
  3. Sign out when done: /fabric\:logout
```

### Already Authenticated
```
$ /fabric:login

🔐 Microsoft Fabric - User Authentication
...

⚠️ You are already signed in.

Current authentication expires: 2025-01-18 15:30:00

Do you want to sign in again? (y/n) n
✅ Keeping existing authentication
```
