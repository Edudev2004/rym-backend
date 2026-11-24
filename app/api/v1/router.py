"""
Enrutador Principal de la API v1
Agrupa todos los sub-routers conforme a los submódulos del documento de arquitectura.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, kardex, consultas

api_router = APIRouter()

# Autenticación y Perfil
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])

# Módulo de Kardex e Inventario (CU06, CU07)
api_router.include_router(kardex.router, prefix="/kardex", tags=["Kardex e Inventario"])

# Módulo de Consultas Multicanal (CU01)
api_router.include_router(consultas.router, prefix="/consultas", tags=["Consultas Multicanal (CU01)"])
