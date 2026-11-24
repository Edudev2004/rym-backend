"""
Enrutador Principal de la API v1
Agrupa todos los sub-routers conforme a los submódulos del documento de arquitectura.
"""
from fastapi import APIRouter

api_router = APIRouter()

# Más adelante se incluirán:
# api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
# api_router.include_router(kardex.router, prefix="/kardex", tags=["Kardex e Inventario"])
# api_router.include_router(pedidos.router, prefix="/pedidos", tags=["Pedidos"])
# api_router.include_router(consultas.router, prefix="/consultas", tags=["Consultas Multicanal"])
# api_router.include_router(produccion.router, prefix="/produccion", tags=["Producción"])
# api_router.include_router(comprobantes.router, prefix="/comprobantes", tags=["Facturación"])
# api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
