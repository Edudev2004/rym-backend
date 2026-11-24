"""
Endpoints REST para Autenticación (/api/v1/auth)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.controllers.ctrl_auth import CtrlAuth
from app.schemas.auth_schema import LoginRequest, TokenResponse, UsuarioResponse
from app.core.security import decode_access_token

router = APIRouter()
security_scheme = HTTPBearer(auto_error=False)

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> str:
    """Dependency para verificar el token JWT y obtener el ID del usuario."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorización ausente"
        )
    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    return payload["sub"]

@router.post("/login", response_model=TokenResponse, summary="Iniciar Sesión")
def login(request: LoginRequest):
    """Inicia sesión con correo y contraseña, retornando token JWT y rol."""
    ctrl = CtrlAuth()
    return ctrl.autenticar(request)

@router.get("/me", response_model=UsuarioResponse, summary="Perfil del Usuario Autenticado")
def get_me(user_id: str = Depends(get_current_user_id)):
    """Retorna los datos del usuario actualmente autenticado."""
    ctrl = CtrlAuth()
    return ctrl.obtener_perfil(user_id)
