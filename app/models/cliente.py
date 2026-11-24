from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Cliente:
    id: Optional[str]
    tipo_documento: str  # DNI, RUC, CE, PASAPORTE
    numero_documento: str
    nombres: str
    apellidos: Optional[str]
    telefono: str
    email: Optional[str] = None
    direccion: Optional[str] = None
    canal_frecuente: str = "WHATSAPP"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def nombre_completo(self) -> str:
        if self.apellidos and self.apellidos.strip():
            return f"{self.nombres.strip()} {self.apellidos.strip()}".strip()
        return self.nombres.strip()

    @property
    def es_empresa(self) -> bool:
        return self.tipo_documento.upper() == "RUC"
