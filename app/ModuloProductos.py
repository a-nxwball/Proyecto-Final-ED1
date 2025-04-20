from datetime import date, timedelta
import sqlite3
import os
try:
    from bd.BDSQLite import conectar_db
except ImportError:
    import sys
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)
    from bd.BDSQLite import conectar_db

class Producto:
    # Modelo de producto
    def __init__(self, id_producto, nombre, descripcion, categoria, precio, stock, fecha_expiracion=None, temporalidad=False, rebaja=0.0, id_proveedor=None):
        self.id_producto = id_producto
        self.nombre = nombre
        self.descripcion = descripcion
        self.categoria = categoria
        self.precio = precio
        self.stock = stock
        self.fecha_expiracion = fecha_expiracion
        self.temporalidad = temporalidad
        self.rebaja = rebaja
        self.id_proveedor = id_proveedor

class NodoProducto:
    # Nodo de lista doblemente enlazada para productos
    def __init__(self, producto):
        self.producto = producto
        self.anterior = None
        self.siguiente = None

class NodoCategoria:
    def __init__(self, categoria):
        self.categoria = categoria
        self.productos_raiz = None  # NodoProducto (inicio de la lista de productos de esta categoría)
        self.siguiente = None
        self.izquierda = None
        self.derecha = None

    def agregar_producto(self, producto):
        nuevo_nodo = NodoProducto(producto)
        if self.productos_raiz is None:
            self.productos_raiz = nuevo_nodo
        else:
            actual = self.productos_raiz
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo
            nuevo_nodo.anterior = actual

class ArbolCategorias:
    def __init__(self):
        self.raiz = None

    def _insertar(self, nodo, categoria):
        if nodo is None:
            return NodoCategoria(categoria)
        if categoria < nodo.categoria:
            nodo.izquierda = self._insertar(nodo.izquierda, categoria)
        elif categoria > nodo.categoria:
            nodo.derecha = self._insertar(nodo.derecha, categoria)
        return nodo

    def insertar_categoria(self, categoria):
        if self.buscar_categoria(categoria) is None:
            self.raiz = self._insertar(self.raiz, categoria)

    def buscar_categoria(self, categoria):
        actual = self.raiz
        while actual:
            if categoria == actual.categoria:
                return actual
            elif categoria < actual.categoria:
                actual = actual.izquierda
            else:
                actual = actual.derecha
        return None

    def agregar_producto_a_categoria(self, producto):
        self.insertar_categoria(producto.categoria)
        nodo_cat = self.buscar_categoria(producto.categoria)
        if nodo_cat:
            nodo_cat.agregar_producto(producto)

    def consultar_productos_por_categoria(self, categoria, limite=5):
        nodo_cat = self.buscar_categoria(categoria)
        productos = []
        if nodo_cat:
            actual = nodo_cat.productos_raiz
            while actual and len(productos) < limite:
                productos.append(actual.producto)
                actual = actual.siguiente
        return productos

    def categorias_disponibles(self):
        res = []
        def inorden(nodo):
            if nodo:
                inorden(nodo.izquierda)
                res.append(nodo.categoria)
                inorden(nodo.derecha)
        inorden(self.raiz)
        return res

class ListaProductos:
    # Lista doblemente enlazada de productos con sincronización a BD
    def __init__(self):
        self.raiz = None
        self.arbol_categorias = ArbolCategorias()
        self._cargar_desde_db()

    def _cargar_desde_db(self):
        # Carga productos desde la base de datos
        self.raiz = None
        conexion = conectar_db()
        if not conexion:
            return
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM Productos")
            filas = cursor.fetchall()
            for fila in filas:
                producto = Producto(
                    id_producto=fila[0], nombre=fila[1], descripcion=fila[2],
                    categoria=fila[3], precio=fila[4], stock=fila[5],
                    fecha_expiracion=fila[6], temporalidad=bool(fila[7]), rebaja=fila[8],
                    id_proveedor=fila[9] if len(fila) > 9 else None
                )
                self._agregar_nodo(producto)
                self.arbol_categorias.agregar_producto_a_categoria(producto)
        except sqlite3.Error as e:
            pass
        finally:
            if conexion:
                conexion.close()

    def _agregar_nodo(self, producto):
        # Agrega un nodo a la lista
        nuevo_nodo = NodoProducto(producto)
        if self.raiz is None:
            self.raiz = nuevo_nodo
        else:
            nodo_actual = self.raiz
            while nodo_actual.siguiente:
                nodo_actual = nodo_actual.siguiente
            nodo_actual.siguiente = nuevo_nodo
            nuevo_nodo.anterior = nodo_actual
        # Agregar al árbol de categorías
        self.arbol_categorias.agregar_producto_a_categoria(producto)
        return nuevo_nodo

    def _mensaje_estado_producto(self, producto):
        # Mensajes automáticos de estado de producto
        mensajes = []
        if producto.fecha_expiracion:
            try:
                fecha_exp = producto.fecha_expiracion
                if isinstance(fecha_exp, str):
                    fecha_exp = date.fromisoformat(fecha_exp)
                dias_restantes = (fecha_exp - date.today()).days
                if 0 <= dias_restantes <= 5:
                    mensajes.append(f"⚠️ El producto '{producto.nombre}' está por expirar en {dias_restantes} día(s).")
            except Exception:
                pass
        if producto.temporalidad:
            mensajes.append(f"🌱 El producto '{producto.nombre}' es de temporada.")
        if producto.rebaja and producto.rebaja > 0:
            mensajes.append(f"💸 El producto '{producto.nombre}' tiene una rebaja activa del {producto.rebaja*100:.0f}%.")
        for m in mensajes:
            print(m)

    def registrar_producto(self, nombre, descripcion, categoria, precio, stock, fecha_expiracion=None, temporalidad=False, rebaja=0.0, id_proveedor=None):
        # Registra un producto en la BD y la lista
        if not fecha_expiracion:
            # Asigna fecha de expiración automática (7 días desde hoy)
            fecha_expiracion = (date.today() + timedelta(days=7)).isoformat()
        conexion = conectar_db()
        if not conexion: return None
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO Productos (nombre, descripcion, categoria, precio, stock, fecha_expiracion, temporalidad, rebaja, id_proveedor)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (nombre, descripcion, categoria, precio, stock, fecha_expiracion, temporalidad, rebaja, id_proveedor))
            id_producto = cursor.lastrowid
            conexion.commit()
            producto = Producto(id_producto, nombre, descripcion, categoria, precio, stock, fecha_expiracion, temporalidad, rebaja, id_proveedor)
            nuevo_nodo = self._agregar_nodo(producto)
            print(f"Producto '{nombre}' registrado con ID: {id_producto}")
            self._mensaje_estado_producto(producto)
            return nuevo_nodo.producto
        except sqlite3.Error as e:
            if conexion: conexion.rollback()
            return None
        finally:
            if conexion: conexion.close()

    def actualizar_producto(self, id_producto, nuevos_datos):
        # Actualiza un producto en la lista y la BD
        nodo_actual = self.raiz
        producto_encontrado = None
        while nodo_actual:
            if nodo_actual.producto.id_producto == id_producto:
                producto_encontrado = nodo_actual.producto
                for clave, valor in nuevos_datos.items():
                    if hasattr(producto_encontrado, clave):
                        setattr(producto_encontrado, clave, valor)
                break
            nodo_actual = nodo_actual.siguiente

        if not producto_encontrado:
            self._cargar_desde_db()
            return False

        conexion = conectar_db()
        if not conexion: return False
        try:
            cursor = conexion.cursor()
            set_clause = ", ".join([f"{clave} = ?" for clave in nuevos_datos])
            valores = list(nuevos_datos.values())
            valores.append(id_producto)
            cursor.execute(f"UPDATE Productos SET {set_clause} WHERE id_producto = ?", valores)
            if cursor.rowcount == 0:
                return False
            conexion.commit()
            print(f"Producto ID {id_producto} actualizado en la BD.")
            return True
        except sqlite3.Error as e:
            if conexion: conexion.rollback()
            return False
        finally:
            if conexion: conexion.close()

    def eliminar_producto(self, id_producto):
        # Elimina un producto de la BD y la lista
        conexion = conectar_db()
        if not conexion: return False
        eliminado_db = False
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM Productos WHERE id_producto = ?", (id_producto,))
            if cursor.rowcount > 0:
                conexion.commit()
                eliminado_db = True
                print(f"Producto ID {id_producto} eliminado de la BD.")
        except sqlite3.Error as e:
            if conexion: conexion.rollback()
            return False
        finally:
            if conexion: conexion.close()

        nodo_actual = self.raiz
        while nodo_actual:
            if nodo_actual.producto.id_producto == id_producto:
                if nodo_actual.anterior:
                    nodo_actual.anterior.siguiente = nodo_actual.siguiente
                else:
                    self.raiz = nodo_actual.siguiente
                if nodo_actual.siguiente:
                    nodo_actual.siguiente.anterior = nodo_actual.anterior
                print(f"Producto ID {id_producto} eliminado de la lista enlazada.")
                return True
            nodo_actual = nodo_actual.siguiente

        if eliminado_db and not nodo_actual:
            self._cargar_desde_db()
            return True
        elif eliminado_db:
            return True
        else:
            return False

    def consultar_producto(self, id_producto=None, nombre=None, solo_rebaja=False):
        # Consulta productos por ID, nombre o rebaja
        resultados = []
        nodo_actual = self.raiz
        while nodo_actual:
            p = nodo_actual.producto
            id_coincide = (id_producto is None or p.id_producto == id_producto)
            nombre_coincide = (nombre is None or p.nombre.lower() == nombre.lower())
            rebaja_coincide = (not solo_rebaja or (p.rebaja > 0))
            if id_coincide and nombre_coincide and rebaja_coincide:
                resultados.append(p)
                self._mensaje_estado_producto(p)
            if id_producto is not None and id_coincide:
                break
            nodo_actual = nodo_actual.siguiente
        return resultados

    def consultar_productos_por_categoria(self, categoria, limite=5):
        return self.arbol_categorias.consultar_productos_por_categoria(categoria, limite)

    def categorias_disponibles(self):
        return self.arbol_categorias.categorias_disponibles()

    def resumen_movimientos_producto(self, movimientos_lista, id_producto, fecha_inicio, fecha_fin, tipo=None):
        # Resumen de movimientos de un producto
        if not movimientos_lista:
            return None
        from app.ModuloTransacciones import ListaTransacciones
        transacciones = ListaTransacciones()
        transacciones_con_producto = []
        nodo = transacciones.raiz
        while nodo:
            if str(id_producto) in [str(pid) for pid in nodo.transaccion.productos]:
                transacciones_con_producto.append(nodo.transaccion.id_transaccion)
            nodo = nodo.siguiente
        resumen = movimientos_lista.resumen_movimientos_por_rango(fecha_inicio, fecha_fin, tipo)
        movimientos_filtrados = [
            m for m in resumen["movimientos"] if m.id_transaccion in transacciones_con_producto
        ]
        return {
            "total_movimientos": len(movimientos_filtrados),
            "movimientos": movimientos_filtrados
        }
