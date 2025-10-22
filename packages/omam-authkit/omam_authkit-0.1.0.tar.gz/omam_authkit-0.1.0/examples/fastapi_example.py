"""
FastAPI integration example for OMAM AuthKit
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from omam_authkit import AuthKitClient
from typing import Dict, Any
import secrets

app = FastAPI(title="OMAM AuthKit FastAPI Example")

# Initialize AuthKit client
client = AuthKitClient(
    client_id="your-client-id",
    client_secret="your-client-secret",
    authkit_url="https://auth.yourdomain.com",
)

# Security scheme for bearer token
security = HTTPBearer()

# In-memory session storage (use Redis or database in production)
sessions = {}


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """
    Verify and decode the access token.

    Args:
        credentials: HTTP Authorization credentials

    Returns:
        User information

    Raises:
        HTTPException: If token is invalid
    """
    try:
        user_info = client.get_user_info(credentials.credentials)
        return user_info
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


@app.get("/")
def home():
    """Home endpoint"""
    return {
        "message": "Welcome to OMAM AuthKit FastAPI Example",
        "login_url": "/login",
        "protected_url": "/protected",
    }


@app.get("/login")
def login(request: Request):
    """Initiate OAuth login flow"""
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)

    # Store state in session (simplified - use proper session management)
    sessions[state] = {"created_at": "now"}

    # Get authorization URL
    auth_url = client.get_authorization_url(
        redirect_uri="http://localhost:8000/callback",
        scopes=["read", "write"],
        state=state,
    )

    return RedirectResponse(url=auth_url)


@app.get("/callback")
def callback(code: str, state: str):
    """Handle OAuth callback"""
    # Verify state
    if state not in sessions:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    # Clean up state
    sessions.pop(state, None)

    try:
        # Exchange code for tokens
        tokens = client.exchange_code_for_tokens(
            code=code, redirect_uri="http://localhost:8000/callback"
        )

        return {
            "message": "Authentication successful",
            "access_token": tokens["access_token"],
            "token_type": "Bearer",
            "instructions": "Use the access_token in Authorization header for protected endpoints",
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/protected")
def protected(user: Dict[str, Any] = Depends(verify_token)):
    """Protected endpoint - requires valid access token"""
    return {
        "message": f"Hello {user['email']}",
        "user": user,
    }


@app.get("/me")
def current_user(user: Dict[str, Any] = Depends(verify_token)):
    """Get current user information"""
    return user


@app.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Revoke access token"""
    try:
        client.revoke_token(credentials.credentials)
        return {"message": "Token revoked successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Optional: Add custom exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom error response"""
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
