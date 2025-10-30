"""
Health check endpoint.
"""
from fastapi import APIRouter
from datetime import datetime
from src.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns service status and basic info.
    """
    return {
        "status": "healthy",
        "service": "spdpay-gateway",
        "version": "1.0.0",
        "environment": settings.env,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/")
async def root():
    """Root endpoint - redirects to docs."""
    return {
        "message": "Spdpay Gateway API",
        "docs": "/docs",
        "health": "/health"
    }
