"""
Entidad de Dominio: Consulta
Representa una solicitud de información, cotización o prospecto multicanal (CU01).
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Consulta:
    id: str
    canal: str # 'WHATSAPP', 'FACEBOOK', 'TIKTOK', 'PRESENCIAL', 'OTRO'
    remitente_nombre: str
    remitente_contacto: str
    mensaje: str
    estado: str = 'PENDIENTE' # 'PENDIENTE', 'ATENDIDA', 'CANCELADA'
    cliente_id: Optional[str] = None
    pedido_id: Optional[str] = None
    usuario_atencion_id: Optional[str] = None
    fecha_recepcion: Optional[datetime] = None
    fecha_atencion: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
