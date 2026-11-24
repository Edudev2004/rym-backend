"""
Entidad de Dominio: Usuario
Representa un trabajador del negocio con uno de los 4 roles permitidos:
ADMINISTRADOR, MARKETING, DISENADOR, OPERADOR
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Usuario:
    id: str
    nombre: str
    correo: str
    password_hash: str
    rol: str # 'ADMINISTRADOR', 'MARKETING', 'DISENADOR', 'OPERADOR'
    activo: bool = True
    ultimo_acceso: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "correo": self.correo,
            "rol": self.rol,
            "activo": self.activo,
            "ultimo_acceso": self.ultimo_acceso.isoformat() if self.ultimo_acceso else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
