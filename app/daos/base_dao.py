"""
Clase Base DAO (Data Access Object)
Encapsula la ejecución de consultas SQL preparadas y pool de conexiones.
Regla de oro: Ninguna sentencia SQL debe existir fuera de los DAOs.
"""
from typing import Any, List, Optional, Dict
import logging
from app.core.database import get_db_cursor

logger = logging.getLogger(__name__)

class BaseDAO:
    """Clase base para todos los Data Access Objects del sistema."""

    def execute_query(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Ejecuta una consulta SQL tipo SELECT y retorna una lista de diccionarios."""
        with get_db_cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchall()

    def execute_query_one(self, sql: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """Ejecuta una consulta SQL tipo SELECT y retorna un solo registro o None."""
        with get_db_cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchone()

    def execute_commit(self, sql: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """Ejecuta INSERT, UPDATE o DELETE y retorna RETURNING si existe."""
        with get_db_cursor() as cursor:
            cursor.execute(sql, params or ())
            try:
                return cursor.fetchone()
            except Exception:
                return None
