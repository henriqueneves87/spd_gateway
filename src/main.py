"""
Spdpay Gateway - Main FastAPI application.
"""
import time
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.core.logger import get_logger
from src.core.exceptions import SpdpayException
from src.api import health
from src.api.v1 import invoices, payments, webhooks, merchants, tokenization

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Spdpay Gateway",
    description="Payment gateway for credit card processing via Adiq",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing."""
    start_time = time.time()
    
    # Log request
    logger.info(f"→ {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log response
    logger.info(
        f"← {request.method} {request.url.path} "
        f"status={response.status_code} duration={duration:.3f}s"
    )
    
    return response


# Exception handler for custom exceptions
@app.exception_handler(SpdpayException)
async def spdpay_exception_handler(request: Request, exc: SpdpayException):
    """Handle custom Spdpay exceptions."""
    logger.error(f"spdpay_exception - code={exc.code}, message={exc.message}, path={request.url.path}")
    
    status_code_map = {
        "UNAUTHORIZED": status.HTTP_401_UNAUTHORIZED,
        "FORBIDDEN": status.HTTP_403_FORBIDDEN,
        "VALIDATION_ERROR": status.HTTP_400_BAD_REQUEST,
        "INVOICE_NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "PAYMENT_NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "MERCHANT_NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "INVALID_STATE_TRANSITION": status.HTTP_400_BAD_REQUEST,
        "ADIQ_ERROR": status.HTTP_502_BAD_GATEWAY,
        "DATABASE_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "PCI_VIOLATION": status.HTTP_400_BAD_REQUEST,
    }
    
    status_code = status_code_map.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": exc.message,
            "code": exc.code
        }
    )


# Include routers
app.include_router(health.router)
app.include_router(invoices.router, prefix="/v1")
app.include_router(payments.router, prefix="/v1")
app.include_router(webhooks.router, prefix="/v1")
app.include_router(merchants.router, prefix="/v1")
app.include_router(tokenization.router, prefix="/v1")


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info(f"spdpay_gateway_starting - env={settings.env}, host={settings.host}, port={settings.port}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("spdpay_gateway_shutting_down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.env == "development"
    )
