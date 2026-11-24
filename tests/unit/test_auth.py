"""
Pruebas Unitarias de Autenticación y Seguridad
Verifica el login para los roles definidos en el informe:
ADMINISTRADOR, MARKETING, DISENADOR, OPERADOR
"""
import pytest
from fastapi import HTTPException
from app.controllers.ctrl_auth import CtrlAuth
from app.schemas.auth_schema import LoginRequest

def test_login_exitoso_administrador():
    ctrl = CtrlAuth()
    response = ctrl.autenticar(
        LoginRequest(correo="admin@rympersonaliza.pe", password="admin123")
    )
    assert response.access_token is not None
    assert response.usuario.correo == "admin@rympersonaliza.pe"
    assert response.usuario.rol == "ADMINISTRADOR"

def test_login_fallido_password_incorrecto():
    ctrl = CtrlAuth()
    with pytest.raises(HTTPException) as exc_info:
        ctrl.autenticar(
            LoginRequest(correo="admin@rympersonaliza.pe", password="password_invalido_xyz")
        )
    assert exc_info.value.status_code == 401

def test_login_fallido_correo_inexistente():
    ctrl = CtrlAuth()
    with pytest.raises(HTTPException) as exc_info:
        ctrl.autenticar(
            LoginRequest(correo="noexiste@rympersonaliza.pe", password="admin123")
        )
    assert exc_info.value.status_code == 401
