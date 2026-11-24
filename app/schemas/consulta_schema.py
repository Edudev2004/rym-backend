"""
Esquemas Pydantic para el Módulo de Consultas Multicanal (CU01)
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ConsultaBase(BaseModel):
    canal: str = Field(default="WHATSAPP", examples=["WHATSAPP"]) # WHATSAPP, FACEBOOK, TIKTOK, PRESENCIAL, OTRO
    remitente_nombre: str = Field(..., examples=["Lucero Falcon"])
    remitente_contacto: str = Field(..., examples=["+51944556677"])
    mensaje: str = Field(..., examples=["Hola, quisiera cotizar 3 tazas mágicas para aniversario."])
    cliente_id: Optional[str] = None

class ConsultaCreateRequest(ConsultaBase):
    pass

class ConsultaUpdateRequest(BaseModel):
    estado: Optional[str] = Field(None, examples=["ATENDIDA"]) # PENDIENTE, ATENDIDA, CANCELADA

class ConsultaResponse(ConsultaBase):
    id: str
    estado: str
    pedido_id: Optional[str] = None
    usuario_atencion_id: Optional[str] = None
    fecha_recepcion: Optional[datetime] = None
    fecha_atencion: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
