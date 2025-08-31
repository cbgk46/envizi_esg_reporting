import logging
from fastapi import Request, HTTPException, status
from typing import Optional
import secrets
from config import USERS

# Get logger for auth module
logger = logging.getLogger("envizi_esg_app.auth")

# Session management (in production, use proper session management)
active_sessions = {}

logger.info(f"Auth module initialized - Available users: {list(USERS.keys())}")
logger.info(f"Active sessions storage initialized")

def get_current_user(request: Request) -> Optional[str]:
    """Get current user from session"""
    session_id = request.cookies.get("session_id")
    client_ip = request.client.host if request.client else 'Unknown'
    
    logger.debug(f"Checking session for client {client_ip}, session_id: {session_id[:10] + '...' if session_id else 'None'}")
    
    if session_id and session_id in active_sessions:
        username = active_sessions[session_id]
        logger.debug(f"Valid session found for user: {username}")
        return username
    
    logger.debug(f"No valid session found for client {client_ip}")
    return None

def create_session(username: str) -> str:
    """Create a new session for user"""
    session_id = secrets.token_urlsafe(32)
    active_sessions[session_id] = username
    
    logger.info(f"New session created for user: {username}, session_id: {session_id[:10]}...")
    logger.debug(f"Total active sessions: {len(active_sessions)}")
    
    return session_id

def require_login(request: Request) -> str:
    """Dependency to require login"""
    client_ip = request.client.host if request.client else 'Unknown'
    user = get_current_user(request)
    
    if not user:
        logger.warning(f"Authentication required - redirecting client {client_ip} to login page")
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            detail="Redirect to login",
            headers={"Location": "/login"}
        )
    
    logger.debug(f"Authentication successful for user: {user} from {client_ip}")
    return user

def authenticate_user(username: str, password: str) -> bool:
    """Authenticate user credentials"""
    logger.info(f"Authentication attempt for username: {username}")
    
    if username not in USERS:
        logger.warning(f"Authentication failed - unknown username: {username}")
        return False
    
    if USERS[username]["password"] != password:
        logger.warning(f"Authentication failed - incorrect password for username: {username}")
        return False
    
    logger.info(f"Authentication successful for username: {username}")
    return True 