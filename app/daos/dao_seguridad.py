"""
DAO de Seguridad y Usuarios (DAOSeguridad)
Conforme a Tabla 1 del informe de diseño:
Entidad: Usuario
Operaciones: autenticar(), findByCorreo(), updatePassword()
"""
from typing import Optional, List
from datetime import datetime, timezone
import logging
from app.daos.base_dao import BaseDAO
from app.models.usuario import Usuario

logger = logging.getLogger(__name__)

# Usuarios iniciales en memoria como fallback cuando la BD Supabase aún no está desplegada
MOCK_USUARIOS = [
    Usuario(
        id="00000000-0000-0000-0000-000000000001",
        nombre="Rommel Navarro (Admin)",
        correo="admin@rympersonaliza.pe",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj404nQ6j8am",
        rol="ADMINISTRADOR",
        activo=True,
        created_at=datetime.now(timezone.utc)
    ),
    Usuario(
        id="00000000-0000-0000-0000-000000000002",
        nombre="Valeria Rios (Marketing)",
        correo="marketing@rympersonaliza.pe",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj404nQ6j8am",
        rol="MARKETING",
        activo=True,
        created_at=datetime.now(timezone.utc)
    ),
    Usuario(
        id="00000000-0000-0000-0000-000000000003",
        nombre="Carlos Mendez (Diseñador)",
        correo="diseno@rympersonaliza.pe",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj404nQ6j8am",
        rol="DISENADOR",
        activo=True,
        created_at=datetime.now(timezone.utc)
    ),
    Usuario(
        id="00000000-0000-0000-0000-000000000004",
        nombre="Jorge Lopez (Operador)",
        correo="produccion@rympersonaliza.pe",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj404nQ6j8am",
        rol="OPERADOR",
        activo=True,
        created_at=datetime.now(timezone.utc)
    ),
]

class DAOSeguridad(BaseDAO):
    """Acceso a datos exclusivo para la entidad Usuario."""

    def findByCorreo(self, correo: str) -> Optional[Usuario]:
        """Busca un usuario por su correo electrónico."""
        sql = """
            SELECT id, nombre, correo, password_hash, rol, activo, ultimo_acceso, created_at, updated_at
            FROM usuarios
            WHERE LOWER(correo) = LOWER(%s) AND activo = TRUE
            LIMIT 1;
        """
        try:
            row = self.execute_query_one(sql, (correo.strip(),))
            if row:
                return Usuario(
                    id=str(row["id"]),
                    nombre=row["nombre"],
                    correo=row["correo"],
                    password_hash=row["password_hash"],
                    rol=row["rol"],
                    activo=row["activo"],
                    ultimo_acceso=row.get("ultimo_acceso"),
                    created_at=row.get("created_at"),
                    updated_at=row.get("updated_at")
                )
        except Exception as e:
            logger.info(f"Fallback a usuarios mock (BD no conectada): {e}")

        # Fallback para pruebas locales
        for u in MOCK_USUARIOS:
            if u.correo.lower() == correo.lower() and u.activo:
                return u
        return None

    def findById(self, id_usuario: str) -> Optional[Usuario]:
        """Busca un usuario por su UUID."""
        sql = """
            SELECT id, nombre, correo, password_hash, rol, activo, ultimo_acceso, created_at, updated_at
            FROM usuarios
            WHERE id = %s AND activo = TRUE
            LIMIT 1;
        """
        try:
            row = self.execute_query_one(sql, (id_usuario,))
            if row:
                return Usuario(
                    id=str(row["id"]),
                    nombre=row["nombre"],
                    correo=row["correo"],
                    password_hash=row["password_hash"],
                    rol=row["rol"],
                    activo=row["activo"],
                    ultimo_acceso=row.get("ultimo_acceso"),
                    created_at=row.get("created_at"),
                    updated_at=row.get("updated_at")
                )
        except Exception:
            pass

        for u in MOCK_USUARIOS:
            if u.id == id_usuario:
                return u
        return None

    def updatePassword(self, id_usuario: str, nuevo_password_hash: str) -> bool:
        """Actualiza el hash de contraseña de un usuario."""
        sql = """
            UPDATE usuarios
            SET password_hash = %s, updated_at = NOW()
            WHERE id = %s;
        """
        try:
            self.execute_commit(sql, (nuevo_password_hash, id_usuario))
            return True
        except Exception as e:
            logger.error(f"Error al actualizar contraseña: {e}")
            return False

    def registrarUltimoAcceso(self, id_usuario: str) -> None:
        """Registra la marca de tiempo del último login exitoso."""
        sql = "UPDATE usuarios SET ultimo_acceso = NOW() WHERE id = %s;"
        try:
            self.execute_commit(sql, (id_usuario,))
        except Exception:
            pass
