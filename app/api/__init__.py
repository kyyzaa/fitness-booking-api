"""
API __init__
"""
from .booking_routes import router as booking_router
from .client_routes import router as client_router
from .trainer_routes import router as trainer_router

__all__ = ['booking_router', 'client_router', 'trainer_router']
