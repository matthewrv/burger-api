from fastapi import APIRouter

__all__ = ("auth_router",)

auth_router = APIRouter(prefix="/auth")
