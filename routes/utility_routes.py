from fastapi import APIRouter

router = APIRouter()

@router.get("/hello")
async def hello():
    """Simple hello endpoint that returns JSON"""
    return {"message": "Hello, World!", "status": "success"}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "FastAPI Sustainability Questionnaire App"} 