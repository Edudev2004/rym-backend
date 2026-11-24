"""
Endpoints REST para el Catálogo de Productos y Recetas (/api/v1/productos)
"""
from typing import List, Optional
from fastapi import APIRouter, Query
from app.controllers.ctrl_producto import CtrlProducto
from app.schemas.producto_schema import (
    ProductoResponse,
    ProductoCreateRequest,
    AsignarRecetaRequest
)

router = APIRouter()

@router.get("", response_model=List[ProductoResponse], summary="Listar Catálogo de Productos")
def listar_productos(
    categoria: Optional[str] = Query(None, description="Filtrar por categoría (SUBLIMADOS, PRENDAS, JOYERIA, ETC.)")
):
    """Retorna los productos disponibles junto con el costo de su receta de insumos y margen estimado."""
    ctrl = CtrlProducto()
    return ctrl.listar_productos(categoria=categoria)

@router.get("/{producto_id}", response_model=ProductoResponse, summary="Obtener Detalle de Producto")
def obtener_producto(producto_id: str):
    """Obtiene un producto y el desglose de su receta de insumos."""
    ctrl = CtrlProducto()
    return ctrl.obtener_producto(producto_id)

@router.post("", response_model=ProductoResponse, status_code=201, summary="Crear Producto (Código Autogenerado)")
def crear_producto(data: ProductoCreateRequest):
    """Crea un nuevo producto en el catálogo y asocia su receta de insumos."""
    ctrl = CtrlProducto()
    return ctrl.crear_producto(data)

@router.put("/{producto_id}/receta", response_model=ProductoResponse, summary="Actualizar Receta de Insumos")
def actualizar_receta(producto_id: str, data: AsignarRecetaRequest):
    """Actualiza los insumos y cantidades requeridas para fabricar el producto."""
    ctrl = CtrlProducto()
    return ctrl.actualizar_receta(producto_id, data)

@router.delete("/{producto_id}", summary="Eliminar Producto")
def eliminar_producto(producto_id: str):
    """Da de baja lógica a un producto."""
    ctrl = CtrlProducto()
    return ctrl.eliminar_producto(producto_id)
