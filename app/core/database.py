"""
Gestor de Conexión a Base de Datos PostgreSQL / Supabase
Cumple con la sección 3.8.1 del informe: Conexión mediante pool de conexiones
y aislamiento estricto de SQL en la capa DAO.
"""
import logging
from contextlib import contextmanager
from typing import Optional, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

# Intentar importar psycopg2 de manera defensiva
try:
    import psycopg2
    from psycopg2 import pool
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    logger.warning("psycopg2 no instalado aún. Se activará modo fallback/mock.")

# Pool de conexiones singleton
_connection_pool: Optional[Any] = None

def init_db_pool():
    """Inicializa el pool de conexiones hacia PostgreSQL/Supabase"""
    global _connection_pool
    if not PSYCOPG2_AVAILABLE:
        return None

    if _connection_pool is None:
        try:
            # Usar DATABASE_URL preferentemente
            if settings.DATABASE_URL and "db.tu-proyecto" not in settings.DATABASE_URL:
                _connection_pool = pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=10,
                    dsn=settings.DATABASE_URL
                )
                logger.info("Pool de conexiones PostgreSQL inicializado exitosamente.")
            else:
                logger.info("DATABASE_URL es placeholder. Esperando credenciales activas de Supabase.")
        except Exception as e:
            logger.warning(f"No se pudo conectar a la BD Supabase todavía: {e}")
            _connection_pool = None
    return _connection_pool

@contextmanager
def get_db_cursor():
    """
    Context manager para obtener un cursor de base de datos desde el pool.
    Garantiza commit automático o rollback en caso de error, y retorno de conexión al pool.
    """
    pool_instance = init_db_pool()
    if pool_instance is None:
        # Modo sin base de datos activa todavía
        raise ConnectionError(
            "Base de datos Supabase aún no conectada o configurada. "
            "Por favor configura tus credenciales en el archivo .env"
        )

    conn = pool_instance.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            yield cursor
            conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Error en transacción SQL: {e}")
        raise e
    finally:
        pool_instance.putconn(conn)
