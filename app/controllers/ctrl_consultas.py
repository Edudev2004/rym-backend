"""
Controlador de Consultas Multicanal (CtrlConsultas)
Orquesta el caso de uso CU01 (Atender consultas multicanal).
"""
from typing import List, Optional
from fastapi import HTTPException, status
from app.daos.dao_consulta import DAOConsulta
from app.schemas.consulta_schema import (
    ConsultaResponse,
    ConsultaCreateRequest,
    ConsultaUpdateRequest
)

class CtrlConsultas:
    """Controlador para la bandeja unificada de consultas."""

    def __init__(self, dao_consulta: Optional[DAOConsulta] = None):
        self.dao = dao_consulta or DAOConsulta()

    def listar_consultas(
        self,
        canal: Optional[str] = None,
        estado: Optional[str] = None
    ) -> List[ConsultaResponse]:
        """Obtiene la lista de consultas con filtros opcionales."""
        consultas = self.dao.findAll(canal=canal, estado=estado)
        return [
            ConsultaResponse(
                id=c.id,
                canal=c.canal,
                remitente_nombre=c.remitente_nombre,
                remitente_contacto=c.remitente_contacto,
                mensaje=c.mensaje,
                estado=c.estado,
                cliente_id=c.cliente_id,
                pedido_id=c.pedido_id,
                usuario_atencion_id=c.usuario_atencion_id,
                fecha_recepcion=c.fecha_recepcion,
                fecha_atencion=c.fecha_atencion,
                created_at=c.created_at,
                updated_at=c.updated_at
            )
            for c in consultas
        ]

    def obtener_consulta(self, consulta_id: str) -> ConsultaResponse:
        """Obtiene el detalle de una consulta específica."""
        c = self.dao.findById(consulta_id)
        if not c:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Consulta {consulta_id} no encontrada"
            )
        return ConsultaResponse(
            id=c.id,
            canal=c.canal,
            remitente_nombre=c.remitente_nombre,
            remitente_contacto=c.remitente_contacto,
            mensaje=c.mensaje,
            estado=c.estado,
            cliente_id=c.cliente_id,
            pedido_id=c.pedido_id,
            usuario_atencion_id=c.usuario_atencion_id,
            fecha_recepcion=c.fecha_recepcion,
            fecha_atencion=c.fecha_atencion,
            created_at=c.created_at,
            updated_at=c.updated_at
        )

    def registrar_consulta(self, data: ConsultaCreateRequest) -> ConsultaResponse:
        """Registra una consulta multicanal manual o recibida por webhook."""
        if not data.remitente_nombre.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre del remitente es obligatorio."
            )
        if not data.mensaje.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El mensaje o detalle de cotización es obligatorio."
            )

        c = self.dao.crear(data)
        return ConsultaResponse(
            id=c.id,
            canal=c.canal,
            remitente_nombre=c.remitente_nombre,
            remitente_contacto=c.remitente_contacto,
            mensaje=c.mensaje,
            estado=c.estado,
            cliente_id=c.cliente_id,
            pedido_id=c.pedido_id,
            usuario_atencion_id=c.usuario_atencion_id,
            fecha_recepcion=c.fecha_recepcion,
            fecha_atencion=c.fecha_atencion,
            created_at=c.created_at,
            updated_at=c.updated_at
        )

    def actualizar_estado(
        self,
        consulta_id: str,
        data: ConsultaUpdateRequest,
        usuario_id: Optional[str] = None
    ) -> ConsultaResponse:
        """Actualiza el estado de la consulta a PENDIENTE, ATENDIDA o CANCELADA."""
        nuevo_estado = data.estado or "ATENDIDA"
        c = self.dao.actualizarEstado(consulta_id, nuevo_estado, usuario_atencion_id=usuario_id)
        if not c:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Consulta {consulta_id} no encontrada"
            )
        return ConsultaResponse(
            id=c.id,
            canal=c.canal,
            remitente_nombre=c.remitente_nombre,
            remitente_contacto=c.remitente_contacto,
            mensaje=c.mensaje,
            estado=c.estado,
            cliente_id=c.cliente_id,
            pedido_id=c.pedido_id,
            usuario_atencion_id=c.usuario_atencion_id,
            fecha_recepcion=c.fecha_recepcion,
            fecha_atencion=c.fecha_atencion,
            created_at=c.created_at,
            updated_at=c.updated_at
        )

    def convertir_a_pedido(
        self,
        consulta_id: str,
        usuario_id: Optional[str] = None
    ) -> dict:
        """
        Transfiere los datos de la consulta para iniciar el registro de pedido (CU01 -> CU02),
        marcando la consulta como ATENDIDA.
        """
        c = self.dao.findById(consulta_id)
        if not c:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Consulta {consulta_id} no encontrada"
            )

        # Marcar la consulta como atendida
        self.dao.actualizarEstado(consulta_id, "ATENDIDA", usuario_atencion_id=usuario_id)

        # Devolver el payload listo para poblar la ficha de nuevo pedido en el frontend
        return {
            "mensaje": "Consulta convertida a pedido con éxito",
            "consulta_id": c.id,
            "cliente_sugerido": {
                "nombres": c.remitente_nombre,
                "telefono": c.remitente_contacto,
                "canal_contacto": c.canal
            },
            "detalle_pedido_sugerido": {
                "canal_origen": c.canal,
                "notas": f"Pedido generado desde consulta: {c.mensaje}"
            }
        }
