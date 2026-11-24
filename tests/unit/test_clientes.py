import pytest
from pydantic import ValidationError
from app.schemas.cliente_schema import ClienteCreateRequest, ClienteUpdateRequest
from app.controllers.ctrl_cliente import CtrlCliente
from app.daos.dao_cliente import DAOCliente, MOCK_CLIENTES
from fastapi import HTTPException

def test_validacion_dni_exito():
    """Valida DNI correcto de 8 dígitos numéricos (PU-05)"""
    req = ClienteCreateRequest(
        tipo_documento="DNI",
        numero_documento="12345678",
        nombres="Juan Carlos",
        apellidos="Pérez Alva",
        telefono="987112233"
    )
    assert req.tipo_documento == "DNI"
    assert req.numero_documento == "12345678"

def test_validacion_dni_falla_longitud_o_letras():
    """Valida rechazo de DNI menor a 8 dígitos o con caracteres alfabéticos (PU-05 / PU-06)"""
    with pytest.raises(ValidationError):
        ClienteCreateRequest(
            tipo_documento="DNI",
            numero_documento="1234567",  # 7 dígitos
            nombres="Pedro",
            telefono="987112233"
        )

    with pytest.raises(ValidationError):
        ClienteCreateRequest(
            tipo_documento="DNI",
            numero_documento="1234567A",  # Con letra
            nombres="Pedro",
            telefono="987112233"
        )

def test_validacion_ruc_exito():
    """Valida RUC correcto de 11 dígitos que inicia con 10 o 20 (PU-06)"""
    req = ClienteCreateRequest(
        tipo_documento="RUC",
        numero_documento="20601234567",
        nombres="Distribuidora Gráfica S.A.C.",
        telefono="998811223"
    )
    assert req.tipo_documento == "RUC"
    assert req.numero_documento == "20601234567"

def test_validacion_ruc_falla_prefijo():
    """Valida rechazo de RUC que no inicie con 10, 20, 15 o 17"""
    with pytest.raises(ValidationError):
        ClienteCreateRequest(
            tipo_documento="RUC",
            numero_documento="30601234567",  # Inicia con 30 (inválido)
            nombres="Empresa Falsa",
            telefono="998811223"
        )

def test_controlador_registrar_y_buscar_cliente():
    """Valida registro, búsqueda y prevención de duplicados"""
    import random
    dao = DAOCliente()
    ctrl = CtrlCliente(dao)

    # Generar DNI aleatorio de 8 dígitos para evitar colisiones con BD real
    num_test = f"78{random.randint(100000, 999999)}"

    req = ClienteCreateRequest(
        tipo_documento="DNI",
        numero_documento=num_test,
        nombres="Rosa Amelia",
        apellidos="Castro Medina",
        telefono="955443322",
        direccion="San Martín de Porres"
    )

    creado = ctrl.registrar_cliente(req)
    assert creado.id is not None
    assert creado.nombre_completo == "Rosa Amelia Castro Medina"

    # Búsqueda por documento
    encontrado = ctrl.buscar_por_documento("DNI", num_test)
    assert encontrado.id == creado.id

    # Intentar duplicar debe fallar con 400
    with pytest.raises(HTTPException) as exc_info:
        ctrl.registrar_cliente(req)
    assert exc_info.value.status_code == 400
