from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from auth import authenticate_user, create_session

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def root():
    """Redirect root to login page"""
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """Handle login form submission"""
    if authenticate_user(username, password):
        session_id = create_session(username)
        response = RedirectResponse(url="/questionnaire", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="session_id", value=session_id, httponly=True, max_age=3600)
        return response
    else:
        return RedirectResponse(url="/login?error=Invalid username or password", status_code=status.HTTP_302_FOUND)

@router.get("/logout")
async def logout():
    """Logout user"""
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("session_id")
    return response 