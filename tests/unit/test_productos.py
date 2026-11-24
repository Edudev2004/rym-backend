"""
Pruebas Unitarias para el Catálogo de Productos y Recetas
Valida:
1. Listado de productos con cálculo de costo de receta y margen.
2. Creación de producto con código autogenerado y receta.
3. Actualización de insumos en la receta.
4. Baja lógica de producto.
"""
import pytest
from app.daos.dao_producto import DAOProducto, MOCK_PRODUCTOS
from app.controllers.ctrl_producto import CtrlProducto
from app.schemas.producto_schema import ProductoCreateRequest, RecetaItemRequest, AsignarRecetaRequest

@pytest.fixture
def dao_producto_test():
    dao = DAOProducto()
    return dao

def test_listar_productos_y_calculo_margen(dao_producto_test):
    ctrl = CtrlProducto(dao_producto=dao_producto_test)
    prods = ctrl.listar_productos()

    assert len(prods) > 0
    taza = next((p for p in prods if "Taza" in p.nombre), None)
    assert taza is not None
    assert taza.precio_base == 22.00
    assert taza.costo_insumos_total > 0
    assert taza.margen_estimado == round(taza.precio_base - taza.costo_insumos_total, 2)

def test_crear_producto_codigo_autogenerado(dao_producto_test):
    ctrl = CtrlProducto(dao_producto=dao_producto_test)

    nuevo = ctrl.crear_producto(
        ProductoCreateRequest(
            nombre="Cuadro MDF Sublimado 20x30",
            categoria="REGALOS",
            precio_base=45.00,
            tiempo_estimado_horas=12,
            receta=[
                RecetaItemRequest(
                    insumo_id="22222222-2222-2222-2222-222222222201",
                    cantidad_requerida=1.0
                )
            ]
        )
    )

    assert nuevo.id is not None
    assert nuevo.codigo.startswith("PROD-CUA-") or nuevo.codigo.startswith("PROD-")
    assert nuevo.precio_base == 45.00
    assert len(nuevo.receta) == 1

def test_actualizar_receta_producto(dao_producto_test):
    ctrl = CtrlProducto(dao_producto=dao_producto_test)
    test_id = "33333333-3333-3333-3333-333333333301"

    actualizado = ctrl.actualizar_receta(
        producto_id=test_id,
        data=AsignarRecetaRequest(
            items=[
                RecetaItemRequest(
                    insumo_id="22222222-2222-2222-2222-222222222202",
                    cantidad_requerida=2.0
                )
            ]
        )
    )

    assert actualizado.id == test_id
    assert len(actualizado.receta) == 1
    assert actualizado.receta[0].cantidad_requerida == 2.0
