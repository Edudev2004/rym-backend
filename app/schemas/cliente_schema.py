from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re

class ClienteCreateRequest(BaseModel):
    tipo_documento: str = Field(..., description="DNI, RUC, CE, PASAPORTE")
    numero_documento: str = Field(..., min_length=4, max_length=20)
    nombres: str = Field(..., min_length=2, max_length=150)
    apellidos: Optional[str] = Field(None, max_length=150)
    telefono: str = Field(..., min_length=7, max_length=20)
    email: Optional[str] = Field(None, max_length=150)
    direccion: Optional[str] = Field(None, max_length=300)
    canal_frecuente: str = Field("WHATSAPP", description="WHATSAPP, FACEBOOK, TIKTOK, TIENDA_FISICA, OTRO")

    @field_validator('tipo_documento')
    @classmethod
    def validar_tipo_doc(cls, v: str) -> str:
        v_upper = v.upper().strip()
        permitidos = ['DNI', 'RUC', 'CE', 'PASAPORTE']
        if v_upper not in permitidos:
            raise ValueError(f"Tipo de documento inválido. Debe ser uno de: {', '.join(permitidos)}")
        return v_upper

    @field_validator('numero_documento')
    @classmethod
    def validar_numero_documento(cls, v: str, info) -> str:
        num = v.strip()
        tipo = info.data.get('tipo_documento', 'DNI')
        
        if tipo == 'DNI':
            if not re.match(r'^\d{8}$', num):
                raise ValueError("El DNI debe contener exactamente 8 dígitos numéricos.")
        elif tipo == 'RUC':
            if not re.match(r'^\d{11}$', num):
                raise ValueError("El RUC debe contener exactamente 11 dígitos numéricos.")
            if not (num.startswith('10') or num.startswith('20') or num.startswith('15') or num.startswith('17')):
                raise ValueError("El RUC debe iniciar con 10, 20, 15 o 17.")
        return num

    @field_validator('telefono')
    @classmethod
    def validar_telefono(cls, v: str) -> str:
        tel = re.sub(r'[\s\-+]', '', v)
        if not tel.isdigit() or len(tel) < 7:
            raise ValueError("El número telefónico debe ser válido y contener al menos 7 dígitos.")
        return v.strip()

class ClienteUpdateRequest(BaseModel):
    nombres: Optional[str] = Field(None, min_length=2, max_length=150)
    apellidos: Optional[str] = Field(None, max_length=150)
    telefono: Optional[str] = Field(None, min_length=7, max_length=20)
    email: Optional[str] = Field(None, max_length=150)
    direccion: Optional[str] = Field(None, max_length=300)
    canal_frecuente: Optional[str] = Field(None)

    @field_validator('telefono')
    @classmethod
    def validar_telefono_opt(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            tel = re.sub(r'[\s\-+]', '', v)
            if not tel.isdigit() or len(tel) < 7:
                raise ValueError("El número telefónico debe ser válido y contener al menos 7 dígitos.")
            return v.strip()
        return v

class ClienteResponse(BaseModel):
    id: str
    tipo_documento: str
    numero_documento: str
    nombres: str
    apellidos: Optional[str] = None
    nombre_completo: str
    telefono: str
    email: Optional[str] = None
    direccion: Optional[str] = None
    canal_frecuente: str
    created_at: Optional[datetime] = None
