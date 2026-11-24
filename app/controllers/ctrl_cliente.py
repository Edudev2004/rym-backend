"""
Controlador de Clientes (CtrlCliente)
Patrón MVC: Orquesta la lógica de negocio y validaciones para Clientes.
"""
from typing import List, Optional
from fastapi import HTTPException, status
from app.daos.dao_cliente import DAOCliente
from app.models.cliente import Cliente
from app.schemas.cliente_schema import ClienteCreateRequest, ClienteUpdateRequest, ClienteResponse

class CtrlCliente:
    def __init__(self, dao_cliente: Optional[DAOCliente] = None):
        self.dao_cliente = dao_cliente or DAOCliente()

    def _mapear_a_response(self, c: Cliente) -> ClienteResponse:
        return ClienteResponse(
            id=c.id,
            tipo_documento=c.tipo_documento,
            numero_documento=c.numero_documento,
            nombres=c.nombres,
            apellidos=c.apellidos,
            nombre_completo=c.nombre_completo,
            telefono=c.telefono,
            email=c.email,
            direccion=c.direccion,
            canal_frecuente=c.canal_frecuente,
            created_at=c.created_at
        )

    def listar_clientes(self, busqueda: Optional[str] = None) -> List[ClienteResponse]:
        """Retorna lista de clientes filtrada o completa."""
        clientes = self.dao_cliente.findAll(busqueda=busqueda)
        return [self._mapear_a_response(c) for c in clientes]

    def obtener_por_id(self, cliente_id: str) -> ClienteResponse:
        """Obtiene un cliente por su identificador UUID."""
        c = self.dao_cliente.findById(cliente_id)
        if not c:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cliente con ID '{cliente_id}' no encontrado."
            )
        return self._mapear_a_response(c)

    def buscar_por_documento(self, tipo_documento: str, numero_documento: str) -> ClienteResponse:
        """Busca cliente por tipo y número de documento (para autocompletado en CU02)."""
        c = self.dao_cliente.findByDocumento(tipo_documento, numero_documento)
        if not c:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró cliente con {tipo_documento} {numero_documento}."
            )
        return self._mapear_a_response(c)

    def registrar_cliente(self, request: ClienteCreateRequest) -> ClienteResponse:
        """
        Registra un nuevo cliente validando la no duplicidad del documento de identidad.
        """
        existente = self.dao_cliente.findByDocumento(request.tipo_documento, request.numero_documento)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un cliente registrado con {request.tipo_documento} {request.numero_documento}."
            )

        nuevo = self.dao_cliente.crear(request)
        return self._mapear_a_response(nuevo)

    def actualizar_cliente(self, cliente_id: str, request: ClienteUpdateRequest) -> ClienteResponse:
        """Actualiza los datos de un cliente."""
        actualizado = self.dao_cliente.actualizar(cliente_id, request)
        if not actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cliente con ID '{cliente_id}' no encontrado para actualizar."
            )
        return self._mapear_a_response(actualizado)

    def eliminar_cliente(self, cliente_id: str) -> dict:
        """Elimina un cliente si no tiene pedidos vinculados."""
        ok = self.dao_cliente.eliminar(cliente_id)
        if not ok:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo eliminar el cliente. Verifique si tiene pedidos registrados."
            )
        return {"mensaje": f"Cliente '{cliente_id}' eliminado con éxito."}
