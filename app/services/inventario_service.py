"""
Servicio de Dominio: InventarioService
Contiene las reglas de negocio para recetas de insumos y descuento automático de kardex
al pasar los pedidos a la fase de producción.
"""
from typing import List, Dict, Any
from app.daos.dao_inventario import DAOInventario, StockInsuficienteException
from app.models.insumo import MovimientoKardex

class InventarioService:
    """Lógica de negocio para inventario y kardex."""

    def __init__(self, dao_inventario: DAOInventario = None):
        self.dao = dao_inventario or DAOInventario()

    def procesar_descuento_produccion(
        self,
        pedido_id: str,
        items_a_descontar: List[Dict[str, Any]],
        usuario_id: str = None
    ) -> List[MovimientoKardex]:
        """
        Descuenta automáticamente los insumos utilizados en un pedido (CU06/t2).
        Valida primero que TODOS los insumos tengan saldo suficiente antes de descontar ninguno.
        """
        # 1. Validación previa de stock (Regla PU-02)
        for item in items_a_descontar:
            insumo_id = item["insumo_id"]
            cantidad = float(item["cantidad"])
            saldo_actual = self.dao.getSaldo(insumo_id)
            if saldo_actual < cantidad:
                insumo = self.dao.findById(insumo_id)
                nombre = insumo.nombre if insumo else insumo_id
                raise StockInsuficienteException(
                    insumo_nombre=nombre,
                    saldo_actual=saldo_actual,
                    cantidad_solicitada=cantidad
                )

        # 2. Ejecutar salidas de kardex (Regla PU-01)
        movimientos_generados = []
        for item in items_a_descontar:
            insumo_id = item["insumo_id"]
            cantidad = float(item["cantidad"])
            mov = self.dao.registrarMovimiento(
                insumo_id=insumo_id,
                tipo_movimiento="SALIDA",
                motivo="PRODUCCION_PEDIDO",
                cantidad=cantidad,
                pedido_id=pedido_id,
                usuario_id=usuario_id,
                observaciones=f"Descuento automático por producción de pedido {pedido_id}"
            )
            movimientos_generados.append(mov)

        return movimientos_generados
