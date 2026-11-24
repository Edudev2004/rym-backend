"""
Entidades de Dominio: Producto y ProductoInsumo (Receta)
Representan el catálogo de artículos personalizados y las recetas de consumo de insumos del kardex.
"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class ProductoInsumo:
    id: str
    producto_id: str
    insumo_id: str
    cantidad_requerida: float
    insumo_codigo: Optional[str] = None
    insumo_nombre: Optional[str] = None
    unidad_medida: Optional[str] = "UND"
    costo_unitario: Optional[float] = 0.0
    created_at: Optional[datetime] = None

@dataclass
class Producto:
    id: str
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    categoria: str = 'SUBLIMADOS' # SUBLIMADOS, PRENDAS, JOYERIA, CORTE_LASER, REGALOS
    precio_base: float = 0.0
    tiempo_estimado_horas: int = 24
    imagen_url: Optional[str] = None
    activo: bool = True
    receta: List[ProductoInsumo] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def costo_insumos_total(self) -> float:
        """Calcula el costo directo de materiales según la receta."""
        total = 0.0
        for item in self.receta:
            costo = item.costo_unitario or 0.0
            total += costo * item.cantidad_requerida
        return round(total, 2)

    @property
    def margen_estimado(self) -> float:
        """Calcula el margen bruto estimado (precio_base - costo_insumos)."""
        return round(self.precio_base - self.costo_insumos_total, 2)
