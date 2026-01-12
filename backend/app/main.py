import time
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
from app.models import QueryResponse
from app.utils import now_ts

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SiliconPulse API",
    description="Strategic Intelligence Backend",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for hackathon simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    
    # If it's the query endpoint, return a safe fallback
    if request.url.path.endswith("/query"):
        return JSONResponse(
            status_code=200,  # Return 200 even on error as requested
            content={
                "query": "Error processing query",
                "evidence": [],
                "signal_strength": 0,
                "last_updated": now_ts()
            }
        )
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": str(exc)}
    )

# Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {process_time:.2f}ms"
    )
    return response

# Include API routes with /api prefix
app.include_router(router, prefix="/api", tags=["api"])

@app.get("/")
async def root():
    return {"message": "SiliconPulse backend running"}

@app.get("/health")
async def health():
    return {"status": "online", "service": "siliconpulse-backend"}
