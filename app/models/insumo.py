"""
Entidades de Dominio: Insumo y MovimientoKardex
Representan los materiales de producción y el historial de transacciones de inventario.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Insumo:
    id: str
    codigo: str
    nombre: str
    unidad_medida: str # 'UND', 'KG', 'L', 'M', etc.
    stock_actual: float
    stock_minimo: float
    costo_unitario: float = 0.0
    descripcion: Optional[str] = None
    activo: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def esta_en_alerta(self) -> bool:
        """Indica si el insumo ha alcanzado o está por debajo del stock mínimo."""
        return self.stock_actual <= self.stock_minimo

    @property
    def estado_alerta(self) -> str:
        """Calcula el nivel de criticidad para el semáforo del Dashboard."""
        if self.stock_actual == 0:
            return "CRITICO_AGOTADO"
        elif self.stock_actual <= (self.stock_minimo / 2):
            return "CRITICO_ROJO"
        elif self.stock_actual <= self.stock_minimo:
            return "ALERTA_AMARILLO"
        return "NORMAL"

@dataclass
class MovimientoKardex:
    id: str
    insumo_id: str
    tipo_movimiento: str # 'ENTRADA', 'SALIDA', 'AJUSTE'
    motivo: str # 'COMPRA', 'PRODUCCION_PEDIDO', 'AJUSTE_INVENTARIO', 'MERMA', 'INVENTARIO_INICIAL'
    cantidad: float
    saldo_anterior: float
    saldo_posterior: float
    pedido_id: Optional[str] = None
    usuario_id: Optional[str] = None
    costo_unitario: float = 0.0
    observaciones: Optional[str] = None
    fecha: Optional[datetime] = None
