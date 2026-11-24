"""
DAO de Clientes (DAOCliente)
Capa de Acceso a Datos estricta para la entidad 'Cliente'.
Conforme al informe de titulación y regla de oro de la arquitectura MVC + DAO:
Ninguna sentencia SQL fuera de los DAOs.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import logging
from app.daos.base_dao import BaseDAO
from app.models.cliente import Cliente
from app.schemas.cliente_schema import ClienteCreateRequest, ClienteUpdateRequest

logger = logging.getLogger(__name__)

# Mock Store en memoria para desarrollo local / pruebas
MOCK_CLIENTES: Dict[str, Cliente] = {
    "11111111-1111-1111-1111-111111111101": Cliente(
        id="11111111-1111-1111-1111-111111111101",
        tipo_documento="DNI",
        numero_documento="72849102",
        nombres="Rommel Eduardo",
        apellidos="Navarro Domínguez",
        telefono="987654321",
        email="rommel.navarro@gmail.com",
        direccion="Av. Perú 2450, San Martín de Porres, Lima",
        canal_frecuente="WHATSAPP",
        created_at=datetime.now(timezone.utc)
    ),
    "11111111-1111-1111-1111-111111111102": Cliente(
        id="11111111-1111-1111-1111-111111111102",
        tipo_documento="DNI",
        numero_documento="45678912",
        nombres="María Elena",
        apellidos="Vásquez Cornejo",
        telefono="912345678",
        email="maria.vasquez@outlook.com",
        direccion="Jr. Las Gardenias 123, Los Olivos, Lima",
        canal_frecuente="WHATSAPP",
        created_at=datetime.now(timezone.utc)
    ),
    "11111111-1111-1111-1111-111111111103": Cliente(
        id="11111111-1111-1111-1111-111111111103",
        tipo_documento="RUC",
        numero_documento="20601234567",
        nombres="Inversiones & Eventos Perú S.A.C.",
        apellidos="",
        telefono="998877665",
        email="contacto@eventosperu.pe",
        direccion="Av. Universitaria 3450, San Martín de Porres, Lima",
        canal_frecuente="WHATSAPP",
        created_at=datetime.now(timezone.utc)
    )
}

class DAOCliente(BaseDAO):

    def findAll(self, busqueda: Optional[str] = None, limite: int = 50) -> List[Cliente]:
        """Obtiene la lista de clientes con opción de búsqueda predictiva."""
        sql = """
            SELECT id, tipo_documento, numero_documento, nombres, apellidos,
                   telefono, email, direccion, canal_frecuente, created_at, updated_at
            FROM clientes
        """
        params: List[Any] = []
        if busqueda and busqueda.strip():
            q = f"%{busqueda.strip()}%"
            sql += """
                WHERE numero_documento ILIKE %s
                   OR nombres ILIKE %s
                   OR apellidos ILIKE %s
                   OR telefono ILIKE %s
            """
            params = [q, q, q, q]

        sql += " ORDER BY created_at DESC LIMIT %s;"
        params.append(limite)

        try:
            rows = self.execute_query(sql, tuple(params))
            return [
                Cliente(
                    id=str(r["id"]),
                    tipo_documento=r["tipo_documento"],
                    numero_documento=r["numero_documento"],
                    nombres=r["nombres"],
                    apellidos=r["apellidos"],
                    telefono=r["telefono"],
                    email=r["email"],
                    direccion=r["direccion"],
                    canal_frecuente=r["canal_frecuente"],
                    created_at=r["created_at"],
                    updated_at=r["updated_at"]
                )
                for r in rows
            ]
        except Exception as e:
            logger.warning(f"Error en BD PostgreSQL al listar clientes: {e}. Usando mock.")

        # Fallback en memoria
        res = list(MOCK_CLIENTES.values())
        if busqueda and busqueda.strip():
            b = busqueda.strip().lower()
            res = [
                c for c in res
                if b in c.numero_documento.lower()
                or b in c.nombres.lower()
                or (c.apellidos and b in c.apellidos.lower())
                or b in c.telefono.lower()
            ]
        return res[:limite]

    def findById(self, cliente_id: str) -> Optional[Cliente]:
        """Busca un cliente por su identificador UUID."""
        sql = """
            SELECT id, tipo_documento, numero_documento, nombres, apellidos,
                   telefono, email, direccion, canal_frecuente, created_at, updated_at
            FROM clientes
            WHERE id = %s;
        """
        try:
            r = self.execute_query_one(sql, (cliente_id,))
            if r:
                return Cliente(
                    id=str(r["id"]),
                    tipo_documento=r["tipo_documento"],
                    numero_documento=r["numero_documento"],
                    nombres=r["nombres"],
                    apellidos=r["apellidos"],
                    telefono=r["telefono"],
                    email=r["email"],
                    direccion=r["direccion"],
                    canal_frecuente=r["canal_frecuente"],
                    created_at=r["created_at"],
                    updated_at=r["updated_at"]
                )
        except Exception as e:
            logger.warning(f"Error BD en findById cliente: {e}. Usando mock.")

        return MOCK_CLIENTES.get(cliente_id)

    def findByDocumento(self, tipo_documento: str, numero_documento: str) -> Optional[Cliente]:
        """Busca un cliente por su tipo y número de documento."""
        tipo_clean = tipo_documento.upper().strip()
        num_clean = numero_documento.strip()

        sql = """
            SELECT id, tipo_documento, numero_documento, nombres, apellidos,
                   telefono, email, direccion, canal_frecuente, created_at, updated_at
            FROM clientes
            WHERE tipo_documento = %s AND numero_documento = %s;
        """
        try:
            r = self.execute_query_one(sql, (tipo_clean, num_clean))
            if r:
                return Cliente(
                    id=str(r["id"]),
                    tipo_documento=r["tipo_documento"],
                    numero_documento=r["numero_documento"],
                    nombres=r["nombres"],
                    apellidos=r["apellidos"],
                    telefono=r["telefono"],
                    email=r["email"],
                    direccion=r["direccion"],
                    canal_frecuente=r["canal_frecuente"],
                    created_at=r["created_at"],
                    updated_at=r["updated_at"]
                )
        except Exception as e:
            logger.warning(f"Error BD en findByDocumento: {e}. Usando mock.")

        for c in MOCK_CLIENTES.values():
            if c.tipo_documento.upper() == tipo_clean and c.numero_documento == num_clean:
                return c
        return None

    def findByTelefono(self, telefono: str) -> Optional[Cliente]:
        """Busca un cliente por su teléfono."""
        tel_clean = telefono.strip()

        sql = """
            SELECT id, tipo_documento, numero_documento, nombres, apellidos,
                   telefono, email, direccion, canal_frecuente, created_at, updated_at
            FROM clientes
            WHERE telefono = %s;
        """
        try:
            r = self.execute_query_one(sql, (tel_clean,))
            if r:
                return Cliente(
                    id=str(r["id"]),
                    tipo_documento=r["tipo_documento"],
                    numero_documento=r["numero_documento"],
                    nombres=r["nombres"],
                    apellidos=r["apellidos"],
                    telefono=r["telefono"],
                    email=r["email"],
                    direccion=r["direccion"],
                    canal_frecuente=r["canal_frecuente"],
                    created_at=r["created_at"],
                    updated_at=r["updated_at"]
                )
        except Exception as e:
            logger.warning(f"Error BD en findByTelefono: {e}. Usando mock.")

        for c in MOCK_CLIENTES.values():
            if c.telefono == tel_clean:
                return c
        return None

    def crear(self, data: ClienteCreateRequest) -> Cliente:
        """Registra un nuevo cliente en el sistema."""
        cliente_id = str(uuid.uuid4())
        ahora = datetime.now(timezone.utc)

        sql = """
            INSERT INTO clientes (
                id, tipo_documento, numero_documento, nombres, apellidos,
                telefono, email, direccion, canal_frecuente, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, created_at;
        """
        try:
            self.execute_commit(sql, (
                cliente_id,
                data.tipo_documento.upper(),
                data.numero_documento.strip(),
                data.nombres.strip(),
                data.apellidos.strip() if data.apellidos else None,
                data.telefono.strip(),
                data.email.strip() if data.email else None,
                data.direccion.strip() if data.direccion else None,
                data.canal_frecuente.upper(),
                ahora,
                ahora
            ))
        except Exception as e:
            logger.warning(f"Error BD al insertar cliente: {e}. Guardando en mock.")

        nuevo = Cliente(
            id=cliente_id,
            tipo_documento=data.tipo_documento.upper(),
            numero_documento=data.numero_documento.strip(),
            nombres=data.nombres.strip(),
            apellidos=data.apellidos.strip() if data.apellidos else "",
            telefono=data.telefono.strip(),
            email=data.email.strip() if data.email else None,
            direccion=data.direccion.strip() if data.direccion else None,
            canal_frecuente=data.canal_frecuente.upper(),
            created_at=ahora,
            updated_at=ahora
        )
        MOCK_CLIENTES[cliente_id] = nuevo
        return nuevo

    def actualizar(self, cliente_id: str, data: ClienteUpdateRequest) -> Optional[Cliente]:
        """Actualiza la información de un cliente existente."""
        existente = self.findById(cliente_id)
        if not existente:
            return None

        ahora = datetime.now(timezone.utc)
        nombres = data.nombres.strip() if data.nombres else existente.nombres
        apellidos = data.apellidos.strip() if data.apellidos is not None else existente.apellidos
        telefono = data.telefono.strip() if data.telefono else existente.telefono
        email = data.email.strip() if data.email is not None else existente.email
        direccion = data.direccion.strip() if data.direccion is not None else existente.direccion
        canal_frecuente = data.canal_frecuente.upper() if data.canal_frecuente else existente.canal_frecuente

        sql = """
            UPDATE clientes
            SET nombres = %s, apellidos = %s, telefono = %s, email = %s,
                direccion = %s, canal_frecuente = %s, updated_at = %s
            WHERE id = %s;
        """
        try:
            self.execute_commit(sql, (nombres, apellidos, telefono, email, direccion, canal_frecuente, ahora, cliente_id))
        except Exception as e:
            logger.warning(f"Error BD al actualizar cliente: {e}.")

        existente.nombres = nombres
        existente.apellidos = apellidos
        existente.telefono = telefono
        existente.email = email
        existente.direccion = direccion
        existente.canal_frecuente = canal_frecuente
        existente.updated_at = ahora
        MOCK_CLIENTES[cliente_id] = existente
        return existente

    def eliminar(self, cliente_id: str) -> bool:
        """Elimina un cliente por su ID."""
        sql = "DELETE FROM clientes WHERE id = %s;"
        try:
            self.execute_commit(sql, (cliente_id,))
            if cliente_id in MOCK_CLIENTES:
                del MOCK_CLIENTES[cliente_id]
            return True
        except Exception as e:
            logger.warning(f"Error BD al eliminar cliente: {e}.")

        if cliente_id in MOCK_CLIENTES:
            del MOCK_CLIENTES[cliente_id]
            return True
        return False
