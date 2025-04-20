from datetime import date, timedelta
import sqlite3
import os # Necesario para construir la ruta a la BD
# Asumiendo que BDSQLite está un nivel arriba y dentro de 'bd'
try:
    from bd.BDSQLite import conectar_db
except ImportError:
     # Intento alternativo si la estructura de carpetas es diferente o se ejecuta desde otro lugar
     # Ajusta la ruta según sea necesario
     import sys
     # Obtener la ruta del directorio padre de 'app'
     current_dir = os.path.dirname(os.path.abspath(__file__))
     parent_dir = os.path.dirname(current_dir)
     # Añadir el directorio padre a sys.path
     sys.path.append(parent_dir)
     from bd.BDSQLite import conectar_db


class Producto:
    def __init__(self, id_producto, nombre, descripcion, categoria, precio, stock, fecha_expiracion=None, temporalidad=False, rebaja=0.0):
        self.id_producto = id_producto
        self.nombre = nombre
        self.descripcion = descripcion
        self.categoria = categoria
        self.precio = precio
        self.stock = stock
        self.fecha_expiracion = fecha_expiracion
        self.temporalidad = temporalidad
        self.rebaja = rebaja

class NodoProducto:
    def __init__(self, producto):
        self.producto = producto
        self.anterior = None
        self.siguiente = None

class ListaProductos:
    def __init__(self):
        self.raiz = None
        self._cargar_desde_db()

    def _cargar_desde_db(self):
        # Limpiar la lista antes de cargar para evitar duplicados
        self.raiz = None
        conexion = conectar_db()
        if not conexion:
            print("Error: No se pudo conectar a la base de datos para cargar productos.")
            return
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM Productos")
            filas = cursor.fetchall()
            for fila in filas:
                # Crear objeto Producto desde la fila de la BD
                producto = Producto(
                    id_producto=fila[0], nombre=fila[1], descripcion=fila[2],
                    categoria=fila[3], precio=fila[4], stock=fila[5],
                    fecha_expiracion=fila[6], temporalidad=bool(fila[7]), rebaja=fila[8]
                )
                # Añadir a la lista enlazada (sin interactuar con la BD aquí)
                self._agregar_nodo(producto)
        except sqlite3.Error as e:
            print(f"Error al cargar productos desde la BD: {e}")
        finally:
            if conexion:
                conexion.close()

    def _agregar_nodo(self, producto):
        # Método auxiliar para añadir nodo a la lista (usado por cargar_desde_db y registrar)
        nuevo_nodo = NodoProducto(producto)
        if self.raiz is None:
            self.raiz = nuevo_nodo
        else:
            nodo_actual = self.raiz
            while nodo_actual.siguiente:
                nodo_actual = nodo_actual.siguiente
            nodo_actual.siguiente = nuevo_nodo
            nuevo_nodo.anterior = nodo_actual
        return nuevo_nodo

    def _mensaje_estado_producto(self, producto):
        mensajes = []
        # Mensaje por expiración próxima (5 días por defecto)
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
        # Mensaje por temporada
        if producto.temporalidad:
            mensajes.append(f"🌱 El producto '{producto.nombre}' es de temporada.")
        # Mensaje por rebaja activa
        if producto.rebaja and producto.rebaja > 0:
            mensajes.append(f"💸 El producto '{producto.nombre}' tiene una rebaja activa del {producto.rebaja*100:.0f}%.")
        for m in mensajes:
            print(m)

    def registrar_producto(self, nombre, descripcion, categoria, precio, stock, fecha_expiracion=None, temporalidad=False, rebaja=0.0):
        # Inserta en la BD primero para obtener el ID
        conexion = conectar_db()
        if not conexion: return None
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO Productos (nombre, descripcion, categoria, precio, stock, fecha_expiracion, temporalidad, rebaja)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (nombre, descripcion, categoria, precio, stock, fecha_expiracion, temporalidad, rebaja))
            id_producto = cursor.lastrowid # Obtener el ID autogenerado
            conexion.commit()

            # Crear objeto Producto y añadir a la lista enlazada
            producto = Producto(id_producto, nombre, descripcion, categoria, precio, stock, fecha_expiracion, temporalidad, rebaja)
            nuevo_nodo = self._agregar_nodo(producto)
            print(f"Producto '{nombre}' registrado con ID: {id_producto}")
            # Mensajes automáticos
            self._mensaje_estado_producto(producto)
            return nuevo_nodo.producto # Devolver el objeto producto creado
        except sqlite3.Error as e:
            print(f"Error al registrar producto en la BD: {e}")
            if conexion: conexion.rollback()
            return None
        finally:
            if conexion: conexion.close()


    def actualizar_producto(self, id_producto, nuevos_datos):
        # Actualiza en la lista enlazada y luego en la BD
        nodo_actual = self.raiz
        producto_encontrado = None
        while nodo_actual:
            if nodo_actual.producto.id_producto == id_producto:
                producto_encontrado = nodo_actual.producto
                # Actualizar objeto en memoria
                for clave, valor in nuevos_datos.items():
                    if hasattr(producto_encontrado, clave):
                        setattr(producto_encontrado, clave, valor)
                    else:
                        print(f"Advertencia: El atributo '{clave}' no existe en Producto.")
                break # Producto encontrado y actualizado en memoria
            nodo_actual = nodo_actual.siguiente

        if not producto_encontrado:
            print(f"Error: Producto con ID {id_producto} no encontrado en la lista. Sincronizando desde BD...")
            self._cargar_desde_db()
            return False

        # Actualizar en la BD
        conexion = conectar_db()
        if not conexion: return False
        try:
            cursor = conexion.cursor()
            # Construir la sentencia UPDATE dinámicamente (cuidado con SQL injection si las claves vienen de fuera)
            set_clause = ", ".join([f"{clave} = ?" for clave in nuevos_datos])
            valores = list(nuevos_datos.values())
            valores.append(id_producto)
            cursor.execute(f"UPDATE Productos SET {set_clause} WHERE id_producto = ?", valores)
            if cursor.rowcount == 0:
                print(f"Advertencia: Producto ID {id_producto} no encontrado en la BD al intentar actualizar.")
                return False
            conexion.commit()
            print(f"Producto ID {id_producto} actualizado en la BD.")
            return True
        except sqlite3.Error as e:
            print(f"Error al actualizar producto ID {id_producto} en la BD: {e}")
            if conexion: conexion.rollback()
            # Considerar revertir el cambio en memoria si la BD falla? Depende del requisito.
            return False
        finally:
            if conexion: conexion.close()


    def eliminar_producto(self, id_producto):
        # Elimina de la BD y luego de la lista enlazada
        conexion = conectar_db()
        if not conexion: return False
        eliminado_db = False
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM Productos WHERE id_producto = ?", (id_producto,))
            # Verificar si se eliminó alguna fila
            if cursor.rowcount > 0:
                 conexion.commit()
                 eliminado_db = True
                 print(f"Producto ID {id_producto} eliminado de la BD.")
            else:
                 print(f"Advertencia: Producto ID {id_producto} no encontrado en la BD.")
                 # Podría existir en la lista pero no en la BD (inconsistencia), o no existir en absoluto.
        except sqlite3.Error as e:
            print(f"Error al eliminar producto ID {id_producto} de la BD: {e}")
            if conexion: conexion.rollback()
            return False # No continuar si falla la BD
        finally:
            if conexion: conexion.close()

        # Si se eliminó de la BD (o no existía en la BD), intentar eliminar de la lista
        nodo_actual = self.raiz
        while nodo_actual:
            if nodo_actual.producto.id_producto == id_producto:
                if nodo_actual.anterior:
                    nodo_actual.anterior.siguiente = nodo_actual.siguiente
                else: # Es la raíz
                    self.raiz = nodo_actual.siguiente
                if nodo_actual.siguiente:
                    nodo_actual.siguiente.anterior = nodo_actual.anterior
                print(f"Producto ID {id_producto} eliminado de la lista enlazada.")
                return True # Eliminado de la lista (y ya se intentó en BD)
            nodo_actual = nodo_actual.siguiente

        # Si llega aquí, no se encontró en la lista enlazada
        if eliminado_db and not nodo_actual:
            print(f"Advertencia: Producto ID {id_producto} eliminado de BD pero no encontrado en la lista. Sincronizando desde BD...")
            self._cargar_desde_db()
            return True
        elif eliminado_db:
             print(f"Advertencia: Producto ID {id_producto} eliminado de BD pero no encontrado en la lista.")
             return True # Se considera éxito porque se eliminó de la BD
        else:
             print(f"Error: Producto ID {id_producto} no encontrado ni en BD ni en lista.")
             return False


    def consultar_producto(self, id_producto=None, nombre=None, solo_rebaja=False):
        resultados = []
        nodo_actual = self.raiz
        while nodo_actual:
            p = nodo_actual.producto
            id_coincide = (id_producto is None or p.id_producto == id_producto)
            nombre_coincide = (nombre is None or p.nombre.lower() == nombre.lower())
            rebaja_coincide = (not solo_rebaja or (p.rebaja > 0))

            if id_coincide and nombre_coincide and rebaja_coincide:
                resultados.append(p)
                # Mensajes automáticos al consultar
                self._mensaje_estado_producto(p)
            
            if id_producto is not None and id_coincide:
                break
                
            nodo_actual = nodo_actual.siguiente
        return resultados

    def resumen_movimientos_producto(self, movimientos_lista, id_producto, fecha_inicio, fecha_fin, tipo=None):
        """
        Devuelve un resumen de movimientos de un producto específico en un rango de fechas y por tipo.
        movimientos_lista: instancia de ListaMovimientos.
        """
        if not movimientos_lista:
            print("Debe proporcionar una instancia de ListaMovimientos.")
            return None
        # Buscar transacciones que incluyan este producto
        from app.ModuloTransacciones import ListaTransacciones
        transacciones = ListaTransacciones()
        transacciones_con_producto = []
        nodo = transacciones.raiz
        while nodo:
            if str(id_producto) in [str(pid) for pid in nodo.transaccion.productos]:
                transacciones_con_producto.append(nodo.transaccion.id_transaccion)
            nodo = nodo.siguiente
        # Filtrar movimientos por esas transacciones
        resumen = movimientos_lista.resumen_movimientos_por_rango(fecha_inicio, fecha_fin, tipo)
        movimientos_filtrados = [
            m for m in resumen["movimientos"] if m.id_transaccion in transacciones_con_producto
        ]
        return {
            "total_movimientos": len(movimientos_filtrados),
            "movimientos": movimientos_filtrados
        }
