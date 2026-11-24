"""
DAO de Consultas Multicanal (DAOConsulta)
Conforme a Tabla 1 del informe de diseño:
Entidad: Consulta
Operaciones: registrarConsulta(), updateEstado(), findByCanal(), findById()
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import logging
from app.daos.base_dao import BaseDAO
from app.models.consulta import Consulta
from app.schemas.consulta_schema import ConsultaCreateRequest

logger = logging.getLogger(__name__)

# Mock Store en memoria para desarrollo local
MOCK_CONSULTAS: Dict[str, Consulta] = {
    "44444444-4444-4444-4444-444444444401": Consulta(
        id="44444444-4444-4444-4444-444444444401",
        canal="WHATSAPP",
        remitente_nombre="Lucero Falcon",
        remitente_contacto="+51944556677",
        mensaje="Hola, buenas tardes, quisiera cotizar 3 tazas mágicas para aniversario con fotos familiares.",
        estado="PENDIENTE",
        fecha_recepcion=datetime.now(timezone.utc)
    ),
    "44444444-4444-4444-4444-444444444402": Consulta(
        id="44444444-4444-4444-4444-444444444402",
        canal="FACEBOOK",
        remitente_nombre="Marcos Benitez",
        remitente_contacto="fb.me/mbenitez99",
        mensaje="Buenas, hacen envíos a San Martín de Porres hoy mismo si pido una taza blanca?",
        estado="PENDIENTE",
        fecha_recepcion=datetime.now(timezone.utc)
    ),
    "44444444-4444-4444-4444-444444444403": Consulta(
        id="44444444-4444-4444-4444-444444444403",
        canal="TIKTOK",
        remitente_nombre="kary_crafts",
        remitente_contacto="@kary_crafts",
        mensaje="Hola vi su video en TikTok del polo con foto de perrito, cuánto demora la entrega?",
        estado="ATENDIDA",
        fecha_recepcion=datetime.now(timezone.utc),
        fecha_atencion=datetime.now(timezone.utc)
    )
}

class DAOConsulta(BaseDAO):
    """Acceso a datos exclusivo para Consultas Multicanal."""

    def findAll(
        self,
        canal: Optional[str] = None,
        estado: Optional[str] = None
    ) -> List[Consulta]:
        """Obtiene la lista de consultas con filtros opcionales por canal y estado."""
        sql = """
            SELECT id, canal, remitente_nombre, remitente_contacto, mensaje, estado,
                   cliente_id, pedido_id, usuario_atencion_id, fecha_recepcion, fecha_atencion, created_at, updated_at
            FROM consultas
            WHERE 1=1
        """
        params: List[Any] = []
        if canal:
            sql += " AND canal = %s"
            params.append(canal.upper())
        if estado:
            sql += " AND estado = %s"
            params.append(estado.upper())

        sql += " ORDER BY fecha_recepcion DESC;"

        try:
            rows = self.execute_query(sql, tuple(params))
            return [
                Consulta(
                    id=str(r["id"]),
                    canal=r["canal"],
                    remitente_nombre=r["remitente_nombre"],
                    remitente_contacto=r["remitente_contacto"],
                    mensaje=r["mensaje"],
                    estado=r["estado"],
                    cliente_id=str(r["cliente_id"]) if r.get("cliente_id") else None,
                    pedido_id=str(r["pedido_id"]) if r.get("pedido_id") else None,
                    usuario_atencion_id=str(r["usuario_atencion_id"]) if r.get("usuario_atencion_id") else None,
                    fecha_recepcion=r.get("fecha_recepcion"),
                    fecha_atencion=r.get("fecha_atencion"),
                    created_at=r.get("created_at"),
                    updated_at=r.get("updated_at")
                )
                for r in rows
            ]
        except Exception as e:
            logger.info(f"Fallback MOCK_CONSULTAS: {e}")
            res = list(MOCK_CONSULTAS.values())
            if canal:
                res = [c for c in res if c.canal.upper() == canal.upper()]
            if estado:
                res = [c for c in res if c.estado.upper() == estado.upper()]
            return res

    def findById(self, consulta_id: str) -> Optional[Consulta]:
        """Busca una consulta por su identificador UUID."""
        sql = """
            SELECT id, canal, remitente_nombre, remitente_contacto, mensaje, estado,
                   cliente_id, pedido_id, usuario_atencion_id, fecha_recepcion, fecha_atencion, created_at, updated_at
            FROM consultas
            WHERE id = %s;
        """
        try:
            r = self.execute_query_one(sql, (consulta_id,))
            if r:
                return Consulta(
                    id=str(r["id"]),
                    canal=r["canal"],
                    remitente_nombre=r["remitente_nombre"],
                    remitente_contacto=r["remitente_contacto"],
                    mensaje=r["mensaje"],
                    estado=r["estado"],
                    cliente_id=str(r["cliente_id"]) if r.get("cliente_id") else None,
                    pedido_id=str(r["pedido_id"]) if r.get("pedido_id") else None,
                    usuario_atencion_id=str(r["usuario_atencion_id"]) if r.get("usuario_atencion_id") else None,
                    fecha_recepcion=r.get("fecha_recepcion"),
                    fecha_atencion=r.get("fecha_atencion"),
                    created_at=r.get("created_at"),
                    updated_at=r.get("updated_at")
                )
        except Exception:
            pass

        return MOCK_CONSULTAS.get(consulta_id)

    def crear(self, data: ConsultaCreateRequest) -> Consulta:
        """Registra una nueva consulta multicanal entrante."""
        sql = """
            INSERT INTO consultas (
                canal, remitente_nombre, remitente_contacto, mensaje, estado, cliente_id, fecha_recepcion
            ) VALUES (%s, %s, %s, %s, 'PENDIENTE', %s, NOW())
            RETURNING id, canal, remitente_nombre, remitente_contacto, mensaje, estado,
                      cliente_id, pedido_id, usuario_atencion_id, fecha_recepcion, fecha_atencion, created_at, updated_at;
        """
        params = (
            data.canal.upper(),
            data.remitente_nombre.strip(),
            data.remitente_contacto.strip(),
            data.mensaje.strip(),
            data.cliente_id
        )
        try:
            r = self.execute_commit(sql, params)
            if r:
                return Consulta(
                    id=str(r["id"]),
                    canal=r["canal"],
                    remitente_nombre=r["remitente_nombre"],
                    remitente_contacto=r["remitente_contacto"],
                    mensaje=r["mensaje"],
                    estado=r["estado"],
                    cliente_id=str(r["cliente_id"]) if r.get("cliente_id") else None,
                    pedido_id=str(r["pedido_id"]) if r.get("pedido_id") else None,
                    usuario_atencion_id=str(r["usuario_atencion_id"]) if r.get("usuario_atencion_id") else None,
                    fecha_recepcion=r.get("fecha_recepcion"),
                    fecha_atencion=r.get("fecha_atencion"),
                    created_at=r.get("created_at"),
                    updated_at=r.get("updated_at")
                )
        except Exception as e:
            logger.info(f"Fallback crear consulta en memoria: {e}")

        new_id = str(uuid.uuid4())
        mock_c = Consulta(
            id=new_id,
            canal=data.canal.upper(),
            remitente_nombre=data.remitente_nombre.strip(),
            remitente_contacto=data.remitente_contacto.strip(),
            mensaje=data.mensaje.strip(),
            estado="PENDIENTE",
            cliente_id=data.cliente_id,
            fecha_recepcion=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        MOCK_CONSULTAS[new_id] = mock_c
        return mock_c

    def actualizarEstado(
        self,
        consulta_id: str,
        nuevo_estado: str,
        usuario_atencion_id: Optional[str] = None
    ) -> Optional[Consulta]:
        """Actualiza el estado de la consulta (PENDIENTE, ATENDIDA, CANCELADA)."""
        sql = """
            UPDATE consultas
            SET estado = %s,
                usuario_atencion_id = COALESCE(%s, usuario_atencion_id),
                fecha_atencion = CASE WHEN %s = 'ATENDIDA' THEN NOW() ELSE fecha_atencion END,
                updated_at = NOW()
            WHERE id = %s
            RETURNING id, canal, remitente_nombre, remitente_contacto, mensaje, estado,
                      cliente_id, pedido_id, usuario_atencion_id, fecha_recepcion, fecha_atencion, created_at, updated_at;
        """
        try:
            r = self.execute_commit(sql, (nuevo_estado.upper(), usuario_atencion_id, nuevo_estado.upper(), consulta_id))
            if r:
                return Consulta(
                    id=str(r["id"]),
                    canal=r["canal"],
                    remitente_nombre=r["remitente_nombre"],
                    remitente_contacto=r["remitente_contacto"],
                    mensaje=r["mensaje"],
                    estado=r["estado"],
                    cliente_id=str(r["cliente_id"]) if r.get("cliente_id") else None,
                    pedido_id=str(r["pedido_id"]) if r.get("pedido_id") else None,
                    usuario_atencion_id=str(r["usuario_atencion_id"]) if r.get("usuario_atencion_id") else None,
                    fecha_recepcion=r.get("fecha_recepcion"),
                    fecha_atencion=r.get("fecha_atencion"),
                    created_at=r.get("created_at"),
                    updated_at=r.get("updated_at")
                )
        except Exception as e:
            logger.info(f"Fallback actualizar estado consulta: {e}")

        if consulta_id in MOCK_CONSULTAS:
            c = MOCK_CONSULTAS[consulta_id]
            c.estado = nuevo_estado.upper()
            if nuevo_estado.upper() == 'ATENDIDA':
                c.fecha_atencion = datetime.now(timezone.utc)
            if usuario_atencion_id:
                c.usuario_atencion_id = usuario_atencion_id
            return c
        return None
