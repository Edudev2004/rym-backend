"""
Esquemas Pydantic para el Catálogo de Productos y Recetas de Insumos
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class RecetaItemRequest(BaseModel):
    insumo_id: str = Field(..., examples=["22222222-2222-2222-2222-222222222202"])
    cantidad_requerida: float = Field(..., gt=0, examples=[1.0])

class RecetaItemResponse(BaseModel):
    id: Optional[str] = None
    insumo_id: str
    insumo_codigo: Optional[str] = None
    insumo_nombre: Optional[str] = None
    unidad_medida: Optional[str] = "UND"
    costo_unitario: Optional[float] = 0.0
    cantidad_requerida: float

class ProductoBase(BaseModel):
    codigo: Optional[str] = Field(None, examples=["PROD-TAZ-01"])
    nombre: str = Field(..., examples=["Taza Mágica Personalizada 11oz"])
    descripcion: Optional[str] = Field(None, examples=["Taza de cerámica que revela diseño con calor"])
    categoria: str = Field(default="SUBLIMADOS", examples=["SUBLIMADOS"]) # SUBLIMADOS, PRENDAS, JOYERIA, CORTE_LASER, REGALOS
    precio_base: float = Field(..., ge=0, examples=[22.00])
    tiempo_estimado_horas: int = Field(default=24, ge=1, examples=[24])
    imagen_url: Optional[str] = None

class ProductoCreateRequest(ProductoBase):
    receta: List[RecetaItemRequest] = []

class AsignarRecetaRequest(BaseModel):
    items: List[RecetaItemRequest]

class ProductoResponse(ProductoBase):
    id: str
    activo: bool
    receta: List[RecetaItemResponse] = []
    costo_insumos_total: float = 0.0
    margen_estimado: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
