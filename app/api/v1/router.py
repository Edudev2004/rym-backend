"""
Enrutador Principal de la API v1
Agrupa todos los sub-routers conforme a los submódulos del documento de arquitectura.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth

api_router = APIRouter()

# Autenticación y Perfil
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])

# Próximos routers a conectar:
# api_router.include_router(kardex.router, prefix="/kardex", tags=["Kardex e Inventario"])
