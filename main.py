from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Initialize Kaleido Chrome for chart generation
import kaleido
kaleido.get_chrome_sync()

from routes.auth_routes import router as auth_router
from routes.questionnaire_routes import router as questionnaire_router

app = FastAPI(
    title="FastAPI Login & Questionnaire",
    description="A FastAPI application with login and questionnaire functionality",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth_router, tags=["authentication"])
app.include_router(questionnaire_router, tags=["questionnaire"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 