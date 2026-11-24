"""
DAO de Inventario y Kardex (DAOInventario)
Conforme a Tabla 1 del informe de diseño:
Entidad: Insumo, MovimientoKardex
Operaciones: registrarMovimiento(), getSaldo(), findAlertas()
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import logging
from app.daos.base_dao import BaseDAO
from app.models.insumo import Insumo, MovimientoKardex

logger = logging.getLogger(__name__)

class StockInsuficienteException(Exception):
    """Excepción lanzada cuando la cantidad a descontar supera el saldo disponible (PU-02)."""
    def __init__(self, insumo_nombre: str, saldo_actual: float, cantidad_solicitada: float):
        self.insumo_nombre = insumo_nombre
        self.saldo_actual = saldo_actual
        self.cantidad_solicitada = cantidad_solicitada
        super().__init__(
            f"Stock insuficiente para el insumo '{insumo_nombre}'. "
            f"Saldo actual: {saldo_actual}, Requerido: {cantidad_solicitada}"
        )

# Mock Store en memoria para desarrollo local antes de conectar Supabase
MOCK_INSUMOS: Dict[str, Insumo] = {
    "22222222-2222-2222-2222-222222222201": Insumo(
        id="22222222-2222-2222-2222-222222222201",
        codigo="INS-TAZ-01",
        nombre="Taza de Cerámica Blanca 11oz",
        unidad_medida="UND",
        stock_actual=25.0,
        stock_minimo=10.0,
        costo_unitario=4.50,
        descripcion="Taza lisa para sublimación"
    ),
    "22222222-2222-2222-2222-222222222202": Insumo(
        id="22222222-2222-2222-2222-222222222202",
        codigo="INS-TAZ-02",
        nombre="Taza Mágica Negra 11oz",
        unidad_medida="UND",
        stock_actual=8.0, # <= stock_minimo (Alerta Amarillo)
        stock_minimo=10.0,
        costo_unitario=8.00,
        descripcion="Taza sensible al calor"
    ),
    "22222222-2222-2222-2222-222222222206": Insumo(
        id="22222222-2222-2222-2222-222222222206",
        codigo="INS-POL-01",
        nombre="Polo Algodón 20/1 Blanco Talla M",
        unidad_medida="UND",
        stock_actual=3.0, # <= 6/2 (Alerta Rojo Crítico)
        stock_minimo=6.0,
        costo_unitario=12.00,
        descripcion="Prenda base estampada"
    )
}

MOCK_MOVIMIENTOS: List[MovimientoKardex] = []

class DAOInventario(BaseDAO):
    """Acceso a datos exclusivo para Insumos y Kardex."""

    def findAll(self) -> List[Insumo]:
        """Obtiene el listado de todos los insumos activos."""
        sql = """
            SELECT id, codigo, nombre, descripcion, unidad_medida, stock_actual, stock_minimo, costo_unitario, activo, created_at, updated_at
            FROM insumos
            WHERE activo = TRUE
            ORDER BY nombre ASC;
        """
        try:
            rows = self.execute_query(sql)
            return [
                Insumo(
                    id=str(r["id"]),
                    codigo=r["codigo"],
                    nombre=r["nombre"],
                    unidad_medida=r["unidad_medida"],
                    stock_actual=float(r["stock_actual"]),
                    stock_minimo=float(r["stock_minimo"]),
                    costo_unitario=float(r["costo_unitario"]),
                    descripcion=r.get("descripcion"),
                    activo=r["activo"],
                    created_at=r.get("created_at"),
                    updated_at=r.get("updated_at")
                )
                for r in rows
            ]
        except Exception as e:
            logger.info(f"Fallback a MOCK_INSUMOS: {e}")
            return list(MOCK_INSUMOS.values())

    def findById(self, insumo_id: str) -> Optional[Insumo]:
        """Busca un insumo por su identificador UUID."""
        sql = """
            SELECT id, codigo, nombre, descripcion, unidad_medida, stock_actual, stock_minimo, costo_unitario, activo, created_at, updated_at
            FROM insumos
            WHERE id = %s AND activo = TRUE;
        """
        try:
            r = self.execute_query_one(sql, (insumo_id,))
            if r:
                return Insumo(
                    id=str(r["id"]),
                    codigo=r["codigo"],
                    nombre=r["nombre"],
                    unidad_medida=r["unidad_medida"],
                    stock_actual=float(r["stock_actual"]),
                    stock_minimo=float(r["stock_minimo"]),
                    costo_unitario=float(r["costo_unitario"]),
                    descripcion=r.get("descripcion"),
                    activo=r["activo"]
                )
        except Exception:
            pass

        return MOCK_INSUMOS.get(insumo_id)

    def getSaldo(self, insumo_id: str) -> float:
        """Operación principal: Obtiene el saldo actual en stock de un insumo."""
        insumo = self.findById(insumo_id)
        if not insumo:
            raise ValueError(f"Insumo {insumo_id} no existe")
        return insumo.stock_actual

    def findAlertas(self) -> List[Insumo]:
        """Operación principal: Retorna los insumos cuyo saldo es menor o igual al stock mínimo."""
        sql = """
            SELECT id, codigo, nombre, descripcion, unidad_medida, stock_actual, stock_minimo, costo_unitario, activo
            FROM insumos
            WHERE activo = TRUE AND stock_actual <= stock_minimo
            ORDER BY stock_actual ASC;
        """
        try:
            rows = self.execute_query(sql)
            return [
                Insumo(
                    id=str(r["id"]),
                    codigo=r["codigo"],
                    nombre=r["nombre"],
                    unidad_medida=r["unidad_medida"],
                    stock_actual=float(r["stock_actual"]),
                    stock_minimo=float(r["stock_minimo"]),
                    costo_unitario=float(r["costo_unitario"]),
                    descripcion=r.get("descripcion")
                )
                for r in rows
            ]
        except Exception:
            pass

        return [i for i in MOCK_INSUMOS.values() if i.esta_en_alerta]

    def registrarMovimiento(
        self,
        insumo_id: str,
        tipo_movimiento: str,
        motivo: str,
        cantidad: float,
        costo_unitario: float = 0.0,
        pedido_id: Optional[str] = None,
        usuario_id: Optional[str] = None,
        observaciones: Optional[str] = None
    ) -> MovimientoKardex:
        """
        Operación principal: Registra un movimiento (ENTRADA, SALIDA o AJUSTE),
        valida la disponibilidad de stock y actualiza el saldo actual en la BD.
        """
        insumo = self.findById(insumo_id)
        if not insumo:
            raise ValueError(f"Insumo {insumo_id} no encontrado")

        saldo_anterior = insumo.stock_actual

        if tipo_movimiento == "ENTRADA":
            saldo_posterior = saldo_anterior + cantidad
        elif tipo_movimiento == "SALIDA":
            if saldo_anterior < cantidad:
                # Regla de Oro PU-02: Lanzar StockInsuficienteException
                raise StockInsuficienteException(
                    insumo_nombre=insumo.nombre,
                    saldo_actual=saldo_anterior,
                    cantidad_solicitada=cantidad
                )
            saldo_posterior = saldo_anterior - cantidad
        elif tipo_movimiento == "AJUSTE":
            saldo_posterior = cantidad
        else:
            raise ValueError(f"Tipo de movimiento inválido: {tipo_movimiento}")

        # Intentar ejecutar en base de datos real
        sql_kardex = """
            INSERT INTO movimientos_kardex (
                insumo_id, tipo_movimiento, motivo, cantidad, saldo_anterior, saldo_posterior,
                pedido_id, usuario_id, costo_unitario, observaciones
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, fecha;
        """
        sql_update = """
            UPDATE insumos
            SET stock_actual = %s, updated_at = NOW()
            WHERE id = %s;
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute(sql_update, (saldo_posterior, insumo_id))
                cursor.execute(sql_kardex, (
                    insumo_id, tipo_movimiento, motivo, cantidad, saldo_anterior, saldo_posterior,
                    pedido_id, usuario_id, costo_unitario, observaciones
                ))
                res = cursor.fetchone()
                mov_id = str(res["id"])
                fecha = res["fecha"]
                return MovimientoKardex(
                    id=mov_id,
                    insumo_id=insumo_id,
                    tipo_movimiento=tipo_movimiento,
                    motivo=motivo,
                    cantidad=cantidad,
                    saldo_anterior=saldo_anterior,
                    saldo_posterior=saldo_posterior,
                    pedido_id=pedido_id,
                    usuario_id=usuario_id,
                    costo_unitario=costo_unitario,
                    observaciones=observaciones,
                    fecha=fecha
                )
        except Exception as e:
            logger.info(f"Fallback movimiento en memoria: {e}")

        # Fallback en memoria para pruebas
        insumo.stock_actual = saldo_posterior
        mov = MovimientoKardex(
            id=str(uuid.uuid4()),
            insumo_id=insumo_id,
            tipo_movimiento=tipo_movimiento,
            motivo=motivo,
            cantidad=cantidad,
            saldo_anterior=saldo_anterior,
            saldo_posterior=saldo_posterior,
            pedido_id=pedido_id,
            usuario_id=usuario_id,
            costo_unitario=costo_unitario,
            observaciones=observaciones,
            fecha=datetime.now(timezone.utc)
        )
        MOCK_MOVIMIENTOS.append(mov)
        return mov

    def getMovimientosByInsumo(self, insumo_id: str) -> List[MovimientoKardex]:
        """Obtiene el historial cronológico de movimientos de un insumo."""
        sql = """
            SELECT id, insumo_id, tipo_movimiento, motivo, cantidad, saldo_anterior, saldo_posterior,
                   pedido_id, observaciones, fecha
            FROM movimientos_kardex
            WHERE insumo_id = %s
            ORDER BY fecha DESC;
        """
        try:
            rows = self.execute_query(sql, (insumo_id,))
            return [
                MovimientoKardex(
                    id=str(r["id"]),
                    insumo_id=str(r["insumo_id"]),
                    tipo_movimiento=r["tipo_movimiento"],
                    motivo=r["motivo"],
                    cantidad=float(r["cantidad"]),
                    saldo_anterior=float(r["saldo_anterior"]),
                    saldo_posterior=float(r["saldo_posterior"]),
                    pedido_id=str(r["pedido_id"]) if r.get("pedido_id") else None,
                    observaciones=r.get("observaciones"),
                    fecha=r.get("fecha")
                )
                for r in rows
            ]
        except Exception:
            pass

        return [m for m in MOCK_MOVIMIENTOS if m.insumo_id == insumo_id]
