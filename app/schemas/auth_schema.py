"""
Esquemas Pydantic para Autenticación y Usuarios
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    correo: EmailStr = Field(..., example="admin@rympersonaliza.pe")
    password: str = Field(..., min_length=4, example="admin123")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: "UsuarioResponse"

class UsuarioResponse(BaseModel):
    id: str
    nombre: str
    correo: str
    rol: str
    activo: bool
    created_at: Optional[datetime] = None

class CambiarPasswordRequest(BaseModel):
    password_actual: str
    password_nueva: str = Field(..., min_length=6)
