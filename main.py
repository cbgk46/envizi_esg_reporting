import os
import sys
import logging
import traceback
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn

from routes.auth_routes import router as auth_router
from routes.questionnaire_routes import router as questionnaire_router

# Configure logging
def setup_logging():
    """Configure comprehensive logging for the application"""
    
    # Get log level from environment variable, default to INFO
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),  # Console output
            logging.FileHandler(f'logs/app_{datetime.now().strftime("%Y%m%d")}.log')  # File output
        ]
    )
    
    # Set specific loggers
    logger = logging.getLogger("envizi_esg_app")
    logger.info(f"Logging configured at {log_level} level")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Environment variables: {dict(os.environ)}")
    
    return logger

# Request logging middleware
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, logger):
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next):
        start_time = datetime.now()
        
        # Log request details
        self.logger.info(
            f"Request: {request.method} {request.url} "
            f"Headers: {dict(request.headers)} "
            f"Client: {request.client.host if request.client else 'Unknown'}"
        )
        
        try:
            response = await call_next(request)
            process_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(
                f"Response: {response.status_code} "
                f"Time: {process_time:.3f}s"
            )
            
            return response
        except Exception as e:
            process_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(
                f"Request failed: {request.method} {request.url} "
                f"Error: {str(e)} "
                f"Time: {process_time:.3f}s "
                f"Traceback: {traceback.format_exc()}"
            )
            raise

# Application lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events"""
    logger = logging.getLogger("envizi_esg_app")
    
    # Startup
    logger.info("=" * 60)
    logger.info("🚀 ESG Reporting Application Starting Up")
    logger.info("=" * 60)
    
    try:
        # Log current working directory and file structure
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info("Directory contents:")
        for item in sorted(os.listdir('.')):
            item_path = os.path.join('.', item)
            if os.path.isdir(item_path):
                logger.info(f"  📁 {item}/")
            else:
                logger.info(f"  📄 {item}")
        
        # Check critical files
        critical_files = [
            'config.py', 'auth.py', 'models.py',
            'routes/auth_routes.py', 'routes/questionnaire_routes.py',
            'templates/login.html', 'templates/questionnaire.html', 'templates/report.html',
            'static/css/styles.css'
        ]
        
        missing_files = []
        for file_path in critical_files:
            if os.path.exists(file_path):
                logger.info(f"✅ {file_path} exists")
            else:
                logger.error(f"❌ {file_path} MISSING")
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"🚨 CRITICAL: Missing files detected: {missing_files}")
        
        # Test imports
        logger.info("Testing critical imports...")
        try:
            import config
            logger.info("✅ config imported successfully")
        except Exception as e:
            logger.error(f"❌ Failed to import config: {e}")
            
        try:
            import auth
            logger.info("✅ auth imported successfully")
        except Exception as e:
            logger.error(f"❌ Failed to import auth: {e}")
        
        # Log environment info
        logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
        logger.info(f"Debug mode: {os.getenv('DEBUG_MODE', 'False')}")
        
        logger.info("✅ Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"💥 Startup failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("🛑 ESG Reporting Application Shutting Down")
    logger.info("=" * 60)

# Initialize logger
app_logger = setup_logging()

app = FastAPI(
    title="FastAPI Login & Questionnaire",
    description="A FastAPI application with login and questionnaire functionality",
    version="1.0.0",
    lifespan=lifespan
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware, logger=app_logger)
# Log middleware addition
app_logger.info("✅ Request logging middleware added")

# Mount static files with error handling
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app_logger.info("✅ Static files mounted successfully")
except Exception as e:
    app_logger.error(f"❌ Failed to mount static files: {e}")
    app_logger.error(f"Traceback: {traceback.format_exc()}")

# Include routers with error handling
try:
    app.include_router(auth_router, tags=["authentication"])
    app_logger.info("✅ Auth router included successfully")
except Exception as e:
    app_logger.error(f"❌ Failed to include auth router: {e}")
    app_logger.error(f"Traceback: {traceback.format_exc()}")

try:
    app.include_router(questionnaire_router, tags=["questionnaire"])
    app_logger.info("✅ Questionnaire router included successfully")
except Exception as e:
    app_logger.error(f"❌ Failed to include questionnaire router: {e}")
    app_logger.error(f"Traceback: {traceback.format_exc()}")

app_logger.info("🎉 FastAPI application configured successfully")

if __name__ == "__main__":
    app_logger.info("🚀 Starting uvicorn server...")
    
    # Get configuration from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '8000'))
    log_level = os.getenv('LOG_LEVEL', 'info').lower()
    
    app_logger.info(f"Server configuration: host={host}, port={port}, log_level={log_level}")
    
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level=log_level,
            access_log=True,
            use_colors=True
        )
    except Exception as e:
        app_logger.error(f"💥 Failed to start uvicorn server: {e}")
        app_logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1) 