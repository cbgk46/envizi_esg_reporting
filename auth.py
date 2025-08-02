from fastapi import Request, HTTPException, status
from typing import Optional
import secrets
from config import USERS

# Session management (in production, use proper session management)
active_sessions = {}

def get_current_user(request: Request) -> Optional[str]:
    """Get current user from session"""
    session_id = request.cookies.get("session_id")
    if session_id and session_id in active_sessions:
        return active_sessions[session_id]
    return None

def create_session(username: str) -> str:
    """Create a new session for user"""
    session_id = secrets.token_urlsafe(32)
    active_sessions[session_id] = username
    return session_id

def require_login(request: Request) -> str:
    """Dependency to require login"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            detail="Redirect to login",
            headers={"Location": "/login"}
        )
    return user

def authenticate_user(username: str, password: str) -> bool:
    """Authenticate user credentials"""
    return username in USERS and USERS[username]["password"] == password 