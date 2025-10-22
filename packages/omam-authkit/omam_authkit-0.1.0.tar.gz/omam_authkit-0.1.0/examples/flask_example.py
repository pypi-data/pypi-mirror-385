"""
Flask integration example for OMAM AuthKit
"""

from flask import Flask, request, session, redirect, jsonify, url_for
from omam_authkit import AuthKitClient
import secrets

app = Flask(__name__)
app.secret_key = "your-secret-key-here"  # Change in production

# Initialize AuthKit client
client = AuthKitClient(
    client_id="your-client-id",
    client_secret="your-client-secret",
    authkit_url="https://auth.yourdomain.com",
)


@app.route("/")
def home():
    """Home page - shows login status"""
    user = session.get("user")
    if user:
        return jsonify({"message": f"Hello {user['email']}", "user": user})
    return jsonify({"message": "Please login", "login_url": "/login"})


@app.route("/login")
def login():
    """Initiate OAuth login flow"""
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state

    # Get authorization URL
    auth_url = client.get_authorization_url(
        redirect_uri="http://localhost:5000/callback",
        scopes=["read", "write"],
        state=state,
    )

    return redirect(auth_url)


@app.route("/callback")
def callback():
    """Handle OAuth callback"""
    code = request.args.get("code")
    state = request.args.get("state")

    # Verify state
    if state != session.get("oauth_state"):
        return jsonify({"error": "Invalid state parameter"}), 400

    session.pop("oauth_state", None)

    try:
        # Exchange code for tokens
        tokens = client.exchange_code_for_tokens(
            code=code, redirect_uri="http://localhost:5000/callback"
        )

        # Store tokens in session
        session["access_token"] = tokens["access_token"]
        session["refresh_token"] = tokens["refresh_token"]

        # Get user info
        user_info = client.get_user_info(tokens["access_token"])
        session["user"] = user_info

        return redirect("/dashboard")

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/dashboard")
def dashboard():
    """Protected dashboard - requires authentication"""
    if "access_token" not in session:
        return redirect("/login")

    user = session.get("user")
    return jsonify(
        {
            "message": "Dashboard",
            "user": user,
            "logout_url": "/logout",
        }
    )


@app.route("/logout")
def logout():
    """Log out the user"""
    # Revoke token (optional)
    if "access_token" in session:
        try:
            client.revoke_token(session["access_token"])
        except:
            pass  # Ignore errors during revocation

    # Clear session
    session.clear()

    return redirect("/")


@app.route("/protected")
def protected():
    """API endpoint protected with token authentication"""
    # Get token from Authorization header
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "No authorization token provided"}), 401

    access_token = auth_header[7:]  # Remove "Bearer " prefix

    try:
        user_info = client.get_user_info(access_token)
        return jsonify({"message": f"Hello {user_info['email']}", "user": user_info})
    except Exception as e:
        return jsonify({"error": "Invalid token"}), 401


if __name__ == "__main__":
    app.run(debug=True, port=5000)
