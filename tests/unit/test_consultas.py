"""
Pruebas Unitarias para el Módulo de Consultas Multicanal (CU01)
Valida:
1. Listado y filtrado por canal y estado.
2. Registro de nueva consulta entrante.
3. Actualización de estado (PENDIENTE -> ATENDIDA).
4. Conversión de consulta a pedido (CU01 -> CU02).
"""
import pytest
from app.models.consulta import Consulta
from app.daos.dao_consulta import DAOConsulta, MOCK_CONSULTAS
from app.controllers.ctrl_consultas import CtrlConsultas
from app.schemas.consulta_schema import ConsultaCreateRequest, ConsultaUpdateRequest

@pytest.fixture
def dao_consultas_test():
    """Fixture con datos de prueba controlados."""
    dao = DAOConsulta()
    test_id = "44444444-4444-4444-4444-444444444499"
    MOCK_CONSULTAS[test_id] = Consulta(
        id=test_id,
        canal="WHATSAPP",
        remitente_nombre="Cliente Test",
        remitente_contacto="+51999888777",
        mensaje="Hola, precio de taza mágica?",
        estado="PENDIENTE"
    )
    return dao, test_id

def test_listar_consultas(dao_consultas_test):
    dao, _ = dao_consultas_test
    ctrl = CtrlConsultas(dao_consulta=dao)

    consultas = ctrl.listar_consultas()
    assert len(consultas) > 0
    assert any(c.canal == "WHATSAPP" for c in consultas)

def test_registrar_nueva_consulta(dao_consultas_test):
    dao, _ = dao_consultas_test
    ctrl = CtrlConsultas(dao_consulta=dao)

    nueva = ctrl.registrar_consulta(
        ConsultaCreateRequest(
            canal="TIKTOK",
            remitente_nombre="Usuario TikTok",
            remitente_contacto="@usuario_tt",
            mensaje="Quiero cotizar 10 polos para promoción escolar."
        )
    )

    assert nueva.id is not None
    assert nueva.canal == "TIKTOK"
    assert nueva.estado == "PENDIENTE"
    assert nueva.remitente_nombre == "Usuario TikTok"

def test_actualizar_estado_consulta(dao_consultas_test):
    dao, test_id = dao_consultas_test
    ctrl = CtrlConsultas(dao_consulta=dao)

    actualizada = ctrl.actualizar_estado(
        consulta_id=test_id,
        data=ConsultaUpdateRequest(estado="ATENDIDA")
    )

    assert actualizada.id == test_id
    assert actualizada.estado == "ATENDIDA"

def test_convertir_consulta_a_pedido(dao_consultas_test):
    dao, test_id = dao_consultas_test
    ctrl = CtrlConsultas(dao_consulta=dao)

    res = ctrl.convertir_a_pedido(consulta_id=test_id)
    assert res["consulta_id"] == test_id
    assert res["cliente_sugerido"]["nombres"] == "Cliente Test"
    assert res["cliente_sugerido"]["telefono"] == "+51999888777"
    assert "taza mágica" in res["detalle_pedido_sugerido"]["notas"]
