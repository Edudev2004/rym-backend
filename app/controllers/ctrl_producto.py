"""
Controlador de Productos y Recetas (CtrlProducto)
Orquesta el catálogo de productos y la vinculación de recetas de insumos del kardex.
"""
from typing import List, Optional
from fastapi import HTTPException, status
from app.daos.dao_producto import DAOProducto
from app.schemas.producto_schema import (
    ProductoResponse,
    ProductoCreateRequest,
    AsignarRecetaRequest,
    RecetaItemResponse
)

class CtrlProducto:
    """Controlador para la gestión del catálogo de productos y recetas."""

    def __init__(self, dao_producto: Optional[DAOProducto] = None):
        self.dao = dao_producto or DAOProducto()

    def _mapear_response(self, p) -> ProductoResponse:
        return ProductoResponse(
            id=p.id,
            codigo=p.codigo,
            nombre=p.nombre,
            descripcion=p.descripcion,
            categoria=p.categoria,
            precio_base=p.precio_base,
            tiempo_estimado_horas=p.tiempo_estimado_horas,
            imagen_url=p.imagen_url,
            activo=p.activo,
            receta=[
                RecetaItemResponse(
                    id=it.id,
                    insumo_id=it.insumo_id,
                    insumo_codigo=it.insumo_codigo,
                    insumo_nombre=it.insumo_nombre,
                    unidad_medida=it.unidad_medida or "UND",
                    costo_unitario=it.costo_unitario or 0.0,
                    cantidad_requerida=it.cantidad_requerida
                )
                for it in p.receta
            ],
            costo_insumos_total=p.costo_insumos_total,
            margen_estimado=p.margen_estimado,
            created_at=p.created_at,
            updated_at=p.updated_at
        )

    def listar_productos(self, categoria: Optional[str] = None) -> List[ProductoResponse]:
        """Obtiene la lista de productos con costos de recetas y márgenes calculados."""
        productos = self.dao.findAll(categoria=categoria)
        return [self._mapear_response(p) for p in productos]

    def obtener_producto(self, producto_id: str) -> ProductoResponse:
        """Obtiene el detalle completo de un producto y su receta."""
        p = self.dao.findById(producto_id)
        if not p:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto {producto_id} no encontrado"
            )
        return self._mapear_response(p)

    def crear_producto(self, data: ProductoCreateRequest) -> ProductoResponse:
        """Crea un nuevo producto en el catálogo y asocia su receta de insumos."""
        if not data.nombre.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre del producto es obligatorio."
            )
        p = self.dao.crear(data)
        return self._mapear_response(p)

    def actualizar_receta(self, producto_id: str, data: AsignarRecetaRequest) -> ProductoResponse:
        """Asigna o actualiza la receta de insumos del producto."""
        p = self.dao.actualizarReceta(producto_id, data.items)
        if not p:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto {producto_id} no encontrado"
            )
        return self._mapear_response(p)

    def eliminar_producto(self, producto_id: str) -> dict:
        """Da de baja lógica a un producto."""
        exito = self.dao.eliminar(producto_id)
        if not exito:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto {producto_id} no encontrado o ya eliminado"
            )
        return {"mensaje": "Producto eliminado exitosamente", "id": producto_id}
