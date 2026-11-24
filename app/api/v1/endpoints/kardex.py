"""
Endpoints REST para Kardex e Inventario (/api/v1/kardex)
"""
from typing import List, Optional
from fastapi import APIRouter, Depends
from app.controllers.ctrl_kardex import CtrlKardex
from app.schemas.kardex_schema import (
    InsumoResponse,
    MovimientoKardexCreate,
    MovimientoKardexResponse,
    AlertaStockResponse,
    DescuentoProduccionRequest
)
from app.api.v1.endpoints.auth import get_current_user_id

router = APIRouter()

@router.get("/insumos", response_model=List[InsumoResponse], summary="Listar Insumos con Saldos")
def listar_insumos():
    """Retorna la lista de insumos con stock actual y estado de alertas."""
    ctrl = CtrlKardex()
    return ctrl.listar_insumos()

@router.get("/insumos/{insumo_id}", response_model=InsumoResponse, summary="Detalle de Insumo")
def obtener_insumo(insumo_id: str):
    """Obtiene el detalle y saldo actual de un insumo."""
    ctrl = CtrlKardex()
    return ctrl.obtener_insumo(insumo_id)

@router.get("/alertas", response_model=List[AlertaStockResponse], summary="Alertas de Stock Mínimo")
def obtener_alertas():
    """Retorna las alertas para el semáforo del Dashboard (rojo y amarillo)."""
    ctrl = CtrlKardex()
    return ctrl.obtener_alertas()

@router.post("/movimientos", response_model=MovimientoKardexResponse, summary="Registrar Entrada/Salida")
def registrar_movimiento(
    data: MovimientoKardexCreate,
    usuario_id: Optional[str] = Depends(get_current_user_id)
):
    """Registra una compra o movimiento manual en el kardex."""
    ctrl = CtrlKardex()
    return ctrl.registrar_movimiento(data, usuario_id=usuario_id)

@router.post("/descuento-produccion", response_model=List[MovimientoKardexResponse], summary="Descuento Automático")
def descuento_por_produccion(
    data: DescuentoProduccionRequest,
    usuario_id: Optional[str] = Depends(get_current_user_id)
):
    """Descuenta del kardex los insumos de una orden en producción (CU06 / t2)."""
    ctrl = CtrlKardex()
    return ctrl.descontar_por_produccion(data, usuario_id=usuario_id)

@router.get("/insumos/{insumo_id}/movimientos", response_model=List[MovimientoKardexResponse], summary="Historial de Movimientos")
def historial_movimientos(insumo_id: str):
    """Retorna el historial completo de entradas y salidas de un insumo."""
    ctrl = CtrlKardex()
    return ctrl.historial_movimientos(insumo_id)
