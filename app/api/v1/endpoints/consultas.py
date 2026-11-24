"""
Endpoints REST para Consultas Multicanal (/api/v1/consultas)
CU01: Atender Consultas (Bandeja unificada y conversión a pedidos)
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.controllers.ctrl_consultas import CtrlConsultas
from app.schemas.consulta_schema import (
    ConsultaResponse,
    ConsultaCreateRequest,
    ConsultaUpdateRequest
)
from app.api.v1.endpoints.auth import get_current_user_id

router = APIRouter()

@router.get("", response_model=List[ConsultaResponse], summary="Listar Consultas Multicanal")
def listar_consultas(
    canal: Optional[str] = Query(None, description="Filtrar por canal (WHATSAPP, FACEBOOK, TIKTOK)"),
    estado: Optional[str] = Query(None, description="Filtrar por estado (PENDIENTE, ATENDIDA, CANCELADA)")
):
    """Retorna la bandeja unificada de consultas entrantes de todos los canales."""
    ctrl = CtrlConsultas()
    return ctrl.listar_consultas(canal=canal, estado=estado)

@router.get("/{consulta_id}", response_model=ConsultaResponse, summary="Obtener Detalle de Consulta")
def obtener_consulta(consulta_id: str):
    """Obtiene el detalle completo de una consulta."""
    ctrl = CtrlConsultas()
    return ctrl.obtener_consulta(consulta_id)

@router.post("", response_model=ConsultaResponse, status_code=201, summary="Registrar Consulta")
def registrar_consulta(data: ConsultaCreateRequest):
    """Registra una nueva consulta recibida por cualquier canal."""
    ctrl = CtrlConsultas()
    return ctrl.registrar_consulta(data)

@router.patch("/{consulta_id}/estado", response_model=ConsultaResponse, summary="Actualizar Estado")
def actualizar_estado(
    consulta_id: str,
    data: ConsultaUpdateRequest,
    usuario_id: Optional[str] = Depends(get_current_user_id)
):
    """Cambia el estado de la consulta (PENDIENTE, ATENDIDA, CANCELADA)."""
    ctrl = CtrlConsultas()
    return ctrl.actualizar_estado(consulta_id, data, usuario_id=usuario_id)

@router.post("/{consulta_id}/convertir", summary="Convertir Consulta a Pedido")
def convertir_a_pedido(
    consulta_id: str,
    usuario_id: Optional[str] = Depends(get_current_user_id)
):
    """Marca la consulta como ATENDIDA y devuelve los datos para precargar en el formulario de pedido (CU01 -> CU02)."""
    ctrl = CtrlConsultas()
    return ctrl.convertir_a_pedido(consulta_id, usuario_id=usuario_id)
