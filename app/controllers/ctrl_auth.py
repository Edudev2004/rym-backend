"""
Controlador de Autenticación y Seguridad (CtrlAuth)
Orquesta el caso de uso de login, validación de credenciales y generación de JWT.
"""
from typing import Optional, Tuple
from fastapi import HTTPException, status
from app.daos.dao_seguridad import DAOSeguridad
from app.models.usuario import Usuario
from app.schemas.auth_schema import LoginRequest, TokenResponse, UsuarioResponse
from app.core.security import verify_password, create_access_token

class CtrlAuth:
    """Controlador para el flujo de autenticación."""

    def __init__(self, dao_seguridad: Optional[DAOSeguridad] = None):
        self.dao = dao_seguridad or DAOSeguridad()

    def autenticar(self, login_data: LoginRequest) -> TokenResponse:
        """Autentica a un usuario y genera su token JWT."""
        usuario = self.dao.findByCorreo(login_data.correo)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos"
            )

        if not usuario.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario se encuentra inactivo en el sistema"
            )

        if not verify_password(login_data.password, usuario.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos"
            )

        # Registrar último acceso
        self.dao.registrarUltimoAcceso(usuario.id)

        # Generar Token JWT
        token = create_access_token(data={
            "sub": usuario.id,
            "correo": usuario.correo,
            "rol": usuario.rol,
            "nombre": usuario.nombre
        })

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            usuario=UsuarioResponse(
                id=usuario.id,
                nombre=usuario.nombre,
                correo=usuario.correo,
                rol=usuario.rol,
                activo=usuario.activo,
                created_at=usuario.created_at
            )
        )

    def obtener_perfil(self, usuario_id: str) -> UsuarioResponse:
        """Obtiene la información de perfil del usuario en sesión."""
        usuario = self.dao.findById(usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return UsuarioResponse(
            id=usuario.id,
            nombre=usuario.nombre,
            correo=usuario.correo,
            rol=usuario.rol,
            activo=usuario.activo,
            created_at=usuario.created_at
        )
