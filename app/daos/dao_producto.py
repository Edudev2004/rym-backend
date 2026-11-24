"""
DAO de Productos y Recetas (DAOProducto)
Conforme a Tabla 1 del informe de diseño:
Entidad: Producto, ProductoInsumo
Operaciones: registrarProducto(), findCatalogo(), getReceta(), updateReceta()
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import re
import logging
from app.daos.base_dao import BaseDAO
from app.models.producto import Producto, ProductoInsumo
from app.schemas.producto_schema import ProductoCreateRequest, RecetaItemRequest

logger = logging.getLogger(__name__)

# Mock Store en memoria para desarrollo local
MOCK_PRODUCTOS: Dict[str, Producto] = {
    "33333333-3333-3333-3333-333333333301": Producto(
        id="33333333-3333-3333-3333-333333333301",
        codigo="PROD-TAZ-01",
        nombre="Taza Mágica Personalizada 11oz",
        descripcion="Taza de cerámica que revela diseño con calor",
        categoria="SUBLIMADOS",
        precio_base=22.00,
        tiempo_estimado_horas=24,
        activo=True,
        receta=[
            ProductoInsumo(
                id="pi-001",
                producto_id="33333333-3333-3333-3333-333333333301",
                insumo_id="22222222-2222-2222-2222-222222222202",
                insumo_codigo="INS-TAZ-02",
                insumo_nombre="Taza Mágica Negra 11oz",
                unidad_medida="UND",
                costo_unitario=8.00,
                cantidad_requerida=1.0
            ),
            ProductoInsumo(
                id="pi-002",
                producto_id="33333333-3333-3333-3333-333333333301",
                insumo_id="22222222-2222-2222-2222-222222222205",
                insumo_codigo="INS-CAJ-01",
                insumo_nombre="Caja Cartón Microcorrugado Taza",
                unidad_medida="UND",
                costo_unitario=1.20,
                cantidad_requerida=1.0
            )
        ]
    ),
    "33333333-3333-3333-3333-333333333302": Producto(
        id="33333333-3333-3333-3333-333333333302",
        codigo="PROD-POL-01",
        nombre="Polo Estampado Algodón 20/1",
        descripcion="Prenda personalizada con vinil o transfer DTF",
        categoria="PRENDAS",
        precio_base=35.00,
        tiempo_estimado_horas=48,
        activo=True,
        receta=[
            ProductoInsumo(
                id="pi-003",
                producto_id="33333333-3333-3333-3333-333333333302",
                insumo_id="22222222-2222-2222-2222-222222222206",
                insumo_codigo="INS-POL-01",
                insumo_nombre="Polo Algodón 20/1 Blanco Talla M",
                unidad_medida="UND",
                costo_unitario=12.00,
                cantidad_requerida=1.0
            )
        ]
    )
}

class DAOProducto(BaseDAO):
    """Acceso a datos exclusivo para el Catálogo de Productos y Recetas."""

    def generar_codigo_autogenerado(self, nombre: str) -> str:
        """Autogenera un código secuencial según la categoría del nombre: PROD-{PREFIJO}-{NUM}."""
        palabras = [p for p in re.sub(r'[^a-zA-Z0-9\s]', '', nombre).upper().split() if len(p) >= 3]
        prefix = palabras[0][:3] if palabras else "GEN"

        sql = "SELECT codigo FROM productos WHERE codigo LIKE %s;"
        codigos = []
        try:
            rows = self.execute_query(sql, (f"PROD-{prefix}-%",))
            codigos = [r["codigo"] for r in rows]
        except Exception:
            pass

        if not codigos:
            codigos = [
                p.codigo for p in MOCK_PRODUCTOS.values()
                if p.codigo.startswith(f"PROD-{prefix}-")
            ]

        max_num = 0
        for cod in codigos:
            m = re.search(r'PROD-[A-Z0-9]+-(\d+)', cod)
            if m:
                try:
                    max_num = max(max_num, int(m.group(1)))
                except ValueError:
                    pass

        siguiente = max_num + 1
        return f"PROD-{prefix}-{siguiente:02d}"

    def findAll(self, categoria: Optional[str] = None) -> List[Producto]:
        """Obtiene el catálogo de productos con sus recetas correspondientes."""
        sql_prod = """
            SELECT id, codigo, nombre, descripcion, categoria, precio_base, tiempo_estimado_horas, imagen_url, activo, created_at, updated_at
            FROM productos
            WHERE activo = TRUE
        """
        params: List[Any] = []
        if categoria and categoria != 'TODOS':
            sql_prod += " AND categoria = %s"
            params.append(categoria.upper())
        sql_prod += " ORDER BY nombre ASC;"

        sql_receta = """
            SELECT pi.id, pi.producto_id, pi.insumo_id, pi.cantidad_requerida,
                   i.codigo AS insumo_codigo, i.nombre AS insumo_nombre, i.unidad_medida, i.costo_unitario
            FROM producto_insumos pi
            JOIN insumos i ON pi.insumo_id = i.id
            ORDER BY pi.created_at ASC;
        """

        try:
            prod_rows = self.execute_query(sql_prod, tuple(params))
            receta_rows = self.execute_query(sql_receta)

            # Agrupar recetas por producto_id
            recetas_by_prod: Dict[str, List[ProductoInsumo]] = {}
            for r in receta_rows:
                p_id = str(r["producto_id"])
                if p_id not in recetas_by_prod:
                    recetas_by_prod[p_id] = []
                recetas_by_prod[p_id].append(
                    ProductoInsumo(
                        id=str(r["id"]),
                        producto_id=p_id,
                        insumo_id=str(r["insumo_id"]),
                        insumo_codigo=r["insumo_codigo"],
                        insumo_nombre=r["insumo_nombre"],
                        unidad_medida=r["unidad_medida"],
                        costo_unitario=float(r["costo_unitario"] or 0.0),
                        cantidad_requerida=float(r["cantidad_requerida"])
                    )
                )

            productos = []
            for r in prod_rows:
                p_id = str(r["id"])
                productos.append(
                    Producto(
                        id=p_id,
                        codigo=r["codigo"],
                        nombre=r["nombre"],
                        descripcion=r.get("descripcion"),
                        categoria=r["categoria"],
                        precio_base=float(r["precio_base"]),
                        tiempo_estimado_horas=int(r["tiempo_estimado_horas"]),
                        imagen_url=r.get("imagen_url"),
                        activo=r["activo"],
                        receta=recetas_by_prod.get(p_id, []),
                        created_at=r.get("created_at"),
                        updated_at=r.get("updated_at")
                    )
                )
            return productos
        except Exception as e:
            logger.info(f"Fallback MOCK_PRODUCTOS: {e}")
            res = [p for p in MOCK_PRODUCTOS.values() if p.activo]
            if categoria and categoria != 'TODOS':
                res = [p for p in res if p.categoria.upper() == categoria.upper()]
            return res

    def findById(self, producto_id: str) -> Optional[Producto]:
        """Busca un producto por su UUID con el desglose de su receta."""
        sql_prod = """
            SELECT id, codigo, nombre, descripcion, categoria, precio_base, tiempo_estimado_horas, imagen_url, activo, created_at, updated_at
            FROM productos
            WHERE id = %s AND activo = TRUE;
        """
        sql_receta = """
            SELECT pi.id, pi.producto_id, pi.insumo_id, pi.cantidad_requerida,
                   i.codigo AS insumo_codigo, i.nombre AS insumo_nombre, i.unidad_medida, i.costo_unitario
            FROM producto_insumos pi
            JOIN insumos i ON pi.insumo_id = i.id
            WHERE pi.producto_id = %s;
        """
        try:
            r = self.execute_query_one(sql_prod, (producto_id,))
            if r:
                receta_rows = self.execute_query(sql_receta, (producto_id,))
                receta = [
                    ProductoInsumo(
                        id=str(it["id"]),
                        producto_id=producto_id,
                        insumo_id=str(it["insumo_id"]),
                        insumo_codigo=it["insumo_codigo"],
                        insumo_nombre=it["insumo_nombre"],
                        unidad_medida=it["unidad_medida"],
                        costo_unitario=float(it["costo_unitario"] or 0.0),
                        cantidad_requerida=float(it["cantidad_requerida"])
                    )
                    for it in receta_rows
                ]
                return Producto(
                    id=str(r["id"]),
                    codigo=r["codigo"],
                    nombre=r["nombre"],
                    descripcion=r.get("descripcion"),
                    categoria=r["categoria"],
                    precio_base=float(r["precio_base"]),
                    tiempo_estimado_horas=int(r["tiempo_estimado_horas"]),
                    imagen_url=r.get("imagen_url"),
                    activo=r["activo"],
                    receta=receta,
                    created_at=r.get("created_at"),
                    updated_at=r.get("updated_at")
                )
        except Exception:
            pass

        return MOCK_PRODUCTOS.get(producto_id)

    def crear(self, data: ProductoCreateRequest) -> Producto:
        """Crea un producto y asocia los insumos de su receta."""
        codigo = data.codigo.strip() if data.codigo and data.codigo.strip() else self.generar_codigo_autogenerado(data.nombre)

        sql_prod = """
            INSERT INTO productos (codigo, nombre, descripcion, categoria, precio_base, tiempo_estimado_horas, imagen_url, activo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
            RETURNING id, codigo, nombre, descripcion, categoria, precio_base, tiempo_estimado_horas, imagen_url, activo, created_at, updated_at;
        """
        params = (
            codigo,
            data.nombre.strip(),
            data.descripcion,
            data.categoria.upper(),
            float(data.precio_base),
            int(data.tiempo_estimado_horas),
            data.imagen_url
        )
        try:
            r = self.execute_commit(sql_prod, params)
            if r:
                p_id = str(r["id"])
                receta_creada = []
                # Insertar receta
                for item in data.receta:
                    sql_pi = """
                        INSERT INTO producto_insumos (producto_id, insumo_id, cantidad_requerida)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (producto_id, insumo_id) DO UPDATE SET cantidad_requerida = EXCLUDED.cantidad_requerida
                        RETURNING id, producto_id, insumo_id, cantidad_requerida;
                    """
                    pi_res = self.execute_commit(sql_pi, (p_id, item.insumo_id, float(item.cantidad_requerida)))
                    if pi_res:
                        receta_creada.append(
                            ProductoInsumo(
                                id=str(pi_res["id"]),
                                producto_id=p_id,
                                insumo_id=str(pi_res["insumo_id"]),
                                cantidad_requerida=float(pi_res["cantidad_requerida"])
                            )
                        )

                return Producto(
                    id=p_id,
                    codigo=r["codigo"],
                    nombre=r["nombre"],
                    descripcion=r.get("descripcion"),
                    categoria=r["categoria"],
                    precio_base=float(r["precio_base"]),
                    tiempo_estimado_horas=int(r["tiempo_estimado_horas"]),
                    imagen_url=r.get("imagen_url"),
                    activo=r["activo"],
                    receta=receta_creada,
                    created_at=r.get("created_at"),
                    updated_at=r.get("updated_at")
                )
        except Exception as e:
            logger.info(f"Fallback crear producto en memoria: {e}")

        new_id = str(uuid.uuid4())
        receta_mock = [
            ProductoInsumo(
                id=str(uuid.uuid4()),
                producto_id=new_id,
                insumo_id=it.insumo_id,
                cantidad_requerida=float(it.cantidad_requerida)
            )
            for it in data.receta
        ]
        prod_mock = Producto(
            id=new_id,
            codigo=codigo,
            nombre=data.nombre.strip(),
            descripcion=data.descripcion,
            categoria=data.categoria.upper(),
            precio_base=float(data.precio_base),
            tiempo_estimado_horas=int(data.tiempo_estimado_horas),
            imagen_url=data.imagen_url,
            activo=True,
            receta=receta_mock,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        MOCK_PRODUCTOS[new_id] = prod_mock
        return prod_mock

    def actualizarReceta(self, producto_id: str, items: List[RecetaItemRequest]) -> Optional[Producto]:
        """Reemplaza la receta de insumos asignada a un producto."""
        sql_del = "DELETE FROM producto_insumos WHERE producto_id = %s;"
        try:
            self.execute_commit(sql_del, (producto_id,))
            for item in items:
                sql_ins = """
                    INSERT INTO producto_insumos (producto_id, insumo_id, cantidad_requerida)
                    VALUES (%s, %s, %s);
                """
                self.execute_commit(sql_ins, (producto_id, item.insumo_id, float(item.cantidad_requerida)))

            return self.findById(producto_id)
        except Exception as e:
            logger.info(f"Fallback actualizar receta en memoria: {e}")

        if producto_id in MOCK_PRODUCTOS:
            p = MOCK_PRODUCTOS[producto_id]
            p.receta = [
                ProductoInsumo(
                    id=str(uuid.uuid4()),
                    producto_id=producto_id,
                    insumo_id=it.insumo_id,
                    cantidad_requerida=float(it.cantidad_requerida)
                )
                for it in items
            ]
            return p
        return None

    def eliminar(self, producto_id: str) -> bool:
        """Da de baja lógica a un producto."""
        sql = "UPDATE productos SET activo = FALSE, updated_at = NOW() WHERE id = %s RETURNING id;"
        try:
            r = self.execute_commit(sql, (producto_id,))
            if r:
                return True
        except Exception as e:
            logger.info(f"Fallback eliminar producto: {e}")

        if producto_id in MOCK_PRODUCTOS:
            MOCK_PRODUCTOS[producto_id].activo = False
            return True
        return False
