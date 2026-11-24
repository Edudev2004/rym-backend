"""
Punto de Entrada Principal - API REST de R&M Personaliza
Arquitectura de 3 Capas (Presentación / PWA -> FastAPI REST -> DAO / PostgreSQL Supabase)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0-mvp",
    description="API de Gestión de Producción, Pedidos, Kardex y Facturación para R&M Personaliza",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Configuración de CORS para acceso desde la PWA (Mobile & Desktop)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir Rutas Principales de la API v1
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "online",
        "app": settings.PROJECT_NAME,
        "version": "1.0.0-mvp",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
