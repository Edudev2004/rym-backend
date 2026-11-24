from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from app.controllers.ctrl_cliente import CtrlCliente
from app.schemas.cliente_schema import ClienteCreateRequest, ClienteUpdateRequest, ClienteResponse
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

def get_ctrl_cliente() -> CtrlCliente:
    return CtrlCliente()

@router.get("/", response_model=List[ClienteResponse], summary="Listar o buscar clientes")
def listar_clientes(
    q: Optional[str] = Query(None, description="Búsqueda por DNI, RUC, nombre, apellido o teléfono"),
    ctrl: CtrlCliente = Depends(get_ctrl_cliente),
    _user = Depends(get_current_user)
):
    return ctrl.listar_clientes(busqueda=q)

@router.get("/buscar/documento", response_model=ClienteResponse, summary="Buscar cliente por documento")
def buscar_por_documento(
    tipo: str = Query(..., description="DNI, RUC, etc."),
    numero: str = Query(..., description="Número de documento"),
    ctrl: CtrlCliente = Depends(get_ctrl_cliente),
    _user = Depends(get_current_user)
):
    return ctrl.buscar_por_documento(tipo, numero)

@router.get("/{cliente_id}", response_model=ClienteResponse, summary="Obtener cliente por ID")
def obtener_cliente(
    cliente_id: str,
    ctrl: CtrlCliente = Depends(get_ctrl_cliente),
    _user = Depends(get_current_user)
):
    return ctrl.obtener_por_id(cliente_id)

@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED, summary="Registrar nuevo cliente")
def crear_cliente(
    request: ClienteCreateRequest,
    ctrl: CtrlCliente = Depends(get_ctrl_cliente),
    _user = Depends(get_current_user)
):
    return ctrl.registrar_cliente(request)

@router.put("/{cliente_id}", response_model=ClienteResponse, summary="Actualizar datos de cliente")
def actualizar_cliente(
    cliente_id: str,
    request: ClienteUpdateRequest,
    ctrl: CtrlCliente = Depends(get_ctrl_cliente),
    _user = Depends(get_current_user)
):
    return ctrl.actualizar_cliente(cliente_id, request)

@router.delete("/{cliente_id}", summary="Eliminar cliente")
def eliminar_cliente(
    cliente_id: str,
    ctrl: CtrlCliente = Depends(get_ctrl_cliente),
    _user = Depends(get_current_user)
):
    return ctrl.eliminar_cliente(cliente_id)
