"""
Esquemas Pydantic para el Módulo de Kardex e Inventario (CU06, CU07)
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class InsumoBase(BaseModel):
    codigo: Optional[str] = Field(None, examples=["INS-TAZ-01"])
    nombre: str = Field(..., examples=["Taza de Cerámica Blanca 11oz"])
    descripcion: Optional[str] = Field(None, examples=["Taza blanca para sublimación"])
    unidad_medida: str = Field(default="UND", examples=["UND"])
    stock_minimo: float = Field(default=5.0, ge=0, examples=[10.0])
    costo_unitario: float = Field(default=0.0, ge=0, examples=[4.50])

class InsumoCreateRequest(InsumoBase):
    stock_inicial: float = Field(default=0.0, ge=0, examples=[25.0])

class InsumoResponse(InsumoBase):
    id: str
    stock_actual: float
    esta_en_alerta: bool
    estado_alerta: str
    activo: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class MovimientoKardexCreate(BaseModel):
    insumo_id: str
    tipo_movimiento: str = Field(..., examples=["ENTRADA"]) # ENTRADA, SALIDA, AJUSTE
    motivo: str = Field(..., examples=["COMPRA"]) # COMPRA, PRODUCCION_PEDIDO, MERMA, AJUSTE_INVENTARIO
    cantidad: float = Field(..., gt=0, examples=[10.0])
    costo_unitario: Optional[float] = Field(0.0, ge=0)
    pedido_id: Optional[str] = None
    observaciones: Optional[str] = Field(None, examples=["Compra de reposición a distribuidora"])

class MovimientoKardexResponse(BaseModel):
    id: str
    insumo_id: str
    tipo_movimiento: str
    motivo: str
    cantidad: float
    saldo_anterior: float
    saldo_posterior: float
    pedido_id: Optional[str] = None
    observaciones: Optional[str] = None
    fecha: Optional[datetime] = None

class AlertaStockResponse(BaseModel):
    id: str
    codigo: str
    nombre: str
    unidad_medida: str
    stock_actual: float
    stock_minimo: float
    estado_alerta: str
    mensaje: str

class DescuentoInsumoItem(BaseModel):
    insumo_id: str
    cantidad: float = Field(..., gt=0)

class DescuentoProduccionRequest(BaseModel):
    pedido_id: str
    items: List[DescuentoInsumoItem]
