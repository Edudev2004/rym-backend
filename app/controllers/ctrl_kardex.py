"""
Controlador de Kardex e Inventario (CtrlKardex)
Conforme al informe de diseño (Sección 3.8.1 y Tabla 39):
Orquesta los casos de uso CU06 (Controlar inventario) y CU07 (Alertas de stock).
"""
from typing import List, Optional
from fastapi import HTTPException, status
from app.daos.dao_inventario import DAOInventario, StockInsuficienteException
from app.services.inventario_service import InventarioService
from app.schemas.kardex_schema import (
    InsumoResponse,
    MovimientoKardexCreate,
    MovimientoKardexResponse,
    AlertaStockResponse,
    DescuentoProduccionRequest
)

class CtrlKardex:
    """Controlador para la gestión de Kardex e Insumos."""

    def __init__(
        self,
        dao_inventario: Optional[DAOInventario] = None,
        service: Optional[InventarioService] = None
    ):
        self.dao = dao_inventario or DAOInventario()
        self.service = service or InventarioService(self.dao)

    def listar_insumos(self) -> List[InsumoResponse]:
        """Obtiene el inventario completo con estado de alertas."""
        insumos = self.dao.findAll()
        return [
            InsumoResponse(
                id=i.id,
                codigo=i.codigo,
                nombre=i.nombre,
                descripcion=i.descripcion,
                unidad_medida=i.unidad_medida,
                stock_actual=i.stock_actual,
                stock_minimo=i.stock_minimo,
                costo_unitario=i.costo_unitario,
                esta_en_alerta=i.esta_en_alerta,
                estado_alerta=i.estado_alerta,
                activo=i.activo,
                created_at=i.created_at,
                updated_at=i.updated_at
            )
            for i in insumos
        ]

    def obtener_insumo(self, insumo_id: str) -> InsumoResponse:
        """Obtiene el detalle y saldo de un insumo."""
        insumo = self.dao.findById(insumo_id)
        if not insumo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Insumo {insumo_id} no encontrado"
            )
        return InsumoResponse(
            id=insumo.id,
            codigo=insumo.codigo,
            nombre=insumo.nombre,
            descripcion=insumo.descripcion,
            unidad_medida=insumo.unidad_medida,
            stock_actual=insumo.stock_actual,
            stock_minimo=insumo.stock_minimo,
            costo_unitario=insumo.costo_unitario,
            esta_en_alerta=insumo.esta_en_alerta,
            estado_alerta=insumo.estado_alerta,
            activo=insumo.activo
        )

    def obtener_alertas(self) -> List[AlertaStockResponse]:
        """Retorna la lista de insumos en nivel crítico o de alerta (PU-03)."""
        insumos_alerta = self.dao.findAlertas()
        alertas = []
        for i in insumos_alerta:
            if i.stock_actual == 0:
                msg = f"¡AGOTADO! Insumo '{i.nombre}' sin existencias."
            elif i.stock_actual <= (i.stock_minimo / 2):
                msg = f"¡CRÍTICO! Saldo ({i.stock_actual}) muy por debajo del mínimo ({i.stock_minimo})."
            else:
                msg = f"Alerta de reposición: Saldo ({i.stock_actual}) llegó al límite ({i.stock_minimo})."

            alertas.append(AlertaStockResponse(
                id=i.id,
                codigo=i.codigo,
                nombre=i.nombre,
                unidad_medida=i.unidad_medida,
                stock_actual=i.stock_actual,
                stock_minimo=i.stock_minimo,
                estado_alerta=i.estado_alerta,
                mensaje=msg
            ))
        return alertas

    def registrar_movimiento(
        self,
        data: MovimientoKardexCreate,
        usuario_id: Optional[str] = None
    ) -> MovimientoKardexResponse:
        """Registra una entrada (compra), salida o ajuste manual en el kardex."""
        try:
            mov = self.dao.registrarMovimiento(
                insumo_id=data.insumo_id,
                tipo_movimiento=data.tipo_movimiento,
                motivo=data.motivo,
                cantidad=data.cantidad,
                costo_unitario=data.costo_unitario or 0.0,
                pedido_id=data.pedido_id,
                usuario_id=usuario_id,
                observaciones=data.observaciones
            )
            return MovimientoKardexResponse(
                id=mov.id,
                insumo_id=mov.insumo_id,
                tipo_movimiento=mov.tipo_movimiento,
                motivo=mov.motivo,
                cantidad=mov.cantidad,
                saldo_anterior=mov.saldo_anterior,
                saldo_posterior=mov.saldo_posterior,
                pedido_id=mov.pedido_id,
                observaciones=mov.observaciones,
                fecha=mov.fecha
            )
        except StockInsuficienteException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    def descontar_por_produccion(
        self,
        request: DescuentoProduccionRequest,
        usuario_id: Optional[str] = None
    ) -> List[MovimientoKardexResponse]:
        """Ejecuta el descuento automático de varios insumos al iniciar producción."""
        try:
            items_dict = [{"insumo_id": item.insumo_id, "cantidad": item.cantidad} for item in request.items]
            movs = self.service.procesar_descuento_produccion(
                pedido_id=request.pedido_id,
                items_a_descontar=items_dict,
                usuario_id=usuario_id
            )
            return [
                MovimientoKardexResponse(
                    id=m.id,
                    insumo_id=m.insumo_id,
                    tipo_movimiento=m.tipo_movimiento,
                    motivo=m.motivo,
                    cantidad=m.cantidad,
                    saldo_anterior=m.saldo_anterior,
                    saldo_posterior=m.saldo_posterior,
                    pedido_id=m.pedido_id,
                    observaciones=m.observaciones,
                    fecha=m.fecha
                )
                for m in movs
            ]
        except StockInsuficienteException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    def historial_movimientos(self, insumo_id: str) -> List[MovimientoKardexResponse]:
        """Retorna el historial cronológico de movimientos de un insumo."""
        movs = self.dao.getMovimientosByInsumo(insumo_id)
        return [
            MovimientoKardexResponse(
                id=m.id,
                insumo_id=m.insumo_id,
                tipo_movimiento=m.tipo_movimiento,
                motivo=m.motivo,
                cantidad=m.cantidad,
                saldo_anterior=m.saldo_anterior,
                saldo_posterior=m.saldo_posterior,
                pedido_id=m.pedido_id,
                observaciones=m.observaciones,
                fecha=m.fecha
            )
            for m in movs
        ]
