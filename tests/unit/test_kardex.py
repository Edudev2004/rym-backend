"""
Pruebas Unitarias del Módulo de Kardex e Inventario
Basadas formalmente en la Tabla 7 (Sección 3.9.3) del informe de entrega final:
- PU-01: Descuento insumo con stock suficiente (cantidad=5, saldo=10 -> saldo_resultante=5)
- PU-02: Descuento con stock insuficiente (cantidad=15, saldo=10 -> Excepción StockInsuficiente)
- PU-03: Alerta al llegar a stock mínimo (saldo = stock_min -> AlertaStock creada)
"""
import pytest
from app.models.insumo import Insumo
from app.daos.dao_inventario import DAOInventario, StockInsuficienteException, MOCK_INSUMOS
from app.controllers.ctrl_kardex import CtrlKardex
from app.schemas.kardex_schema import MovimientoKardexCreate

@pytest.fixture
def dao_test():
    """Fixture para crear un DAO con insumo controlado para pruebas."""
    dao = DAOInventario()
    # Insumo de prueba con UUID válido, saldo inicial = 10.0 y stock mínimo = 5.0
    test_id = "00000000-0000-0000-0000-000000000099"
    MOCK_INSUMOS[test_id] = Insumo(
        id=test_id,
        codigo="INS-TEST-01",
        nombre="Insumo de Prueba PU",
        unidad_medida="UND",
        stock_actual=10.0,
        stock_minimo=5.0,
        costo_unitario=2.50
    )
    return dao, test_id

def test_pu_01_descuento_con_stock_suficiente(dao_test):
    """
    ID: PU-01
    Componente: CtrlKardex / DAOInventario
    Entrada: cantidad=5, saldo=10
    Resultado esperado: saldo_resultante = 5
    """
    dao, insumo_id = dao_test
    ctrl = CtrlKardex(dao_inventario=dao)

    saldo_inicial = dao.getSaldo(insumo_id)
    assert saldo_inicial == 10.0, "El saldo inicial debe ser 10"

    # Registrar salida de 5 unidades
    mov = ctrl.registrar_movimiento(
        MovimientoKardexCreate(
            insumo_id=insumo_id,
            tipo_movimiento="SALIDA",
            motivo="PRODUCCION_PEDIDO",
            cantidad=5.0,
            observaciones="Prueba PU-01"
        )
    )

    saldo_resultante = dao.getSaldo(insumo_id)
    assert saldo_resultante == 5.0, f"Se esperaba saldo 5.0 pero se obtuvo {saldo_resultante}"
    assert mov.saldo_posterior == 5.0

def test_pu_02_descuento_con_stock_insuficiente(dao_test):
    """
    ID: PU-02
    Componente: CtrlKardex / DAOInventario
    Entrada: cantidad=15, saldo=10
    Resultado esperado: Excepción StockInsuficiente
    """
    dao, insumo_id = dao_test
    # Resetear saldo a 10
    MOCK_INSUMOS[insumo_id].stock_actual = 10.0

    # Al intentar registrar salida de 15 cuando solo hay 10, debe lanzar StockInsuficienteException
    with pytest.raises(StockInsuficienteException) as exc_info:
        dao.registrarMovimiento(
            insumo_id=insumo_id,
            tipo_movimiento="SALIDA",
            motivo="PRODUCCION_PEDIDO",
            cantidad=15.0
        )

    assert "Stock insuficiente" in str(exc_info.value)
    # Verificar que el saldo no haya cambiado
    assert dao.getSaldo(insumo_id) == 10.0

def test_pu_03_alerta_al_llegar_a_stock_minimo(dao_test):
    """
    ID: PU-03
    Componente: CtrlKardex
    Entrada: saldo = stock_min (5.0)
    Resultado esperado: AlertaStock creada / detectada en nivel ALERTA_AMARILLO
    """
    dao, _ = dao_test
    ctrl = CtrlKardex(dao_inventario=dao)

    # 1. Validación de la regla a nivel de entidad de dominio
    insumo_alerta = Insumo(
        id="00000000-0000-0000-0000-000000000098",
        codigo="INS-TEST-03",
        nombre="Insumo Test Stock Minimo",
        unidad_medida="UND",
        stock_actual=5.0,
        stock_minimo=5.0
    )
    assert insumo_alerta.esta_en_alerta is True
    assert insumo_alerta.estado_alerta == "ALERTA_AMARILLO"

    # 2. Validación de alertas a nivel de controlador con la base de datos
    alertas = ctrl.obtener_alertas()
    assert len(alertas) > 0, "Debe haber al menos un insumo en alerta en el sistema"
    for a in alertas:
        assert a.stock_actual <= a.stock_minimo
        assert a.estado_alerta in ["ALERTA_AMARILLO", "CRITICO_ROJO", "CRITICO_AGOTADO"]
