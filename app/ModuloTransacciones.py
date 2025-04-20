import sqlite3
import json # Para serializar/deserializar la lista de productos
import os
try:
    from bd.BDSQLite import conectar_db
except ImportError:
     import sys
     current_dir = os.path.dirname(os.path.abspath(__file__))
     parent_dir = os.path.dirname(current_dir)
     sys.path.append(parent_dir)
     from bd.BDSQLite import conectar_db

class NodoTransaccion:
    # Nodo para la lista doblemente enlazada de transacciones
    def __init__(self, transaccion):
        self.transaccion = transaccion
        self.anterior = None
        self.siguiente = None
        
class Transaccion:
    # Representa una transacción de venta
    def __init__(self, id_transaccion, id_cliente, productos, total, fecha, tipo_pago, estado):
        self.id_transaccion = id_transaccion
        self.id_cliente = id_cliente
        self.productos = productos # Lista de IDs o nombres de productos
        self.total = total
        self.fecha = fecha
        self.tipo_pago = tipo_pago
        self.estado = estado # Ej: 'pendiente', 'completada', 'cancelada'

class ListaTransacciones:
    def __init__(self):
        self.raiz = None
        self._cargar_desde_db()

    def _cargar_desde_db(self):
        self.raiz = None
        conexion = conectar_db()
        if not conexion: return
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM Transacciones")
            filas = cursor.fetchall()
            for fila in filas:
                try:
                    # Deserializar productos de JSON a lista Python
                    productos_lista = json.loads(fila[2]) if fila[2] else []
                except json.JSONDecodeError:
                    print(f"Advertencia: Error al decodificar JSON de productos para transacción ID {fila[0]}. Usando lista vacía.")
                    productos_lista = []

                transaccion = Transaccion(
                    id_transaccion=fila[0], id_cliente=fila[1], productos=productos_lista,
                    total=fila[3], fecha=fila[4], tipo_pago=fila[5], estado=fila[6]
                )
                self._agregar_nodo(transaccion)
        except sqlite3.Error as e:
            print(f"Error al cargar transacciones desde la BD: {e}")
        finally:
            if conexion: conexion.close()

    def _agregar_nodo(self, transaccion):
        nuevo_nodo = NodoTransaccion(transaccion)
        if self.raiz is None:
            self.raiz = nuevo_nodo
        else:
            nodo_actual = self.raiz
            while nodo_actual.siguiente is not None:
                nodo_actual = nodo_actual.siguiente
            nodo_actual.siguiente = nuevo_nodo
            nuevo_nodo.anterior = nodo_actual
        return nuevo_nodo

    def registrar_transaccion(self, id_cliente, productos, total, fecha, tipo_pago, estado):
        # Cambiado para aceptar atributos
        conexion = conectar_db()
        if not conexion: return None
        try:
            # Serializar lista de productos a JSON
            productos_json = json.dumps(productos)

            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO Transacciones (id_cliente, productos, total, fecha, tipo_pago, estado)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (id_cliente, productos_json, total, fecha, tipo_pago, estado))
            id_transaccion = cursor.lastrowid
            conexion.commit()

            transaccion = Transaccion(id_transaccion, id_cliente, productos, total, fecha, tipo_pago, estado)
            nuevo_nodo = self._agregar_nodo(transaccion)
            print(f"Transacción registrada con ID: {id_transaccion}")
            return nuevo_nodo.transaccion
        except sqlite3.Error as e:
            print(f"Error al registrar transacción en la BD: {e}")
            if conexion: conexion.rollback()
            return None
        except json.JSONDecodeError as je:
             print(f"Error al serializar productos a JSON: {je}")
             if conexion: conexion.rollback()
             return None
        finally:
            if conexion: conexion.close()

    def actualizar_transaccion(self, id_transaccion, nuevos_datos):
        # Actualiza en memoria
        nodo_actual = self.raiz
        transaccion_encontrada = None
        while nodo_actual:
            if nodo_actual.transaccion.id_transaccion == id_transaccion:
                transaccion_encontrada = nodo_actual.transaccion
                for clave, valor in nuevos_datos.items():
                    setattr(transaccion_encontrada, clave, valor)
                break
            nodo_actual = nodo_actual.siguiente

        if not transaccion_encontrada:
            print(f"Error: Transacción ID {id_transaccion} no encontrada en lista. Sincronizando desde BD...")
            self._cargar_desde_db()
            return False

        # Actualiza en BD
        conexion = conectar_db()
        if not conexion: return False
        try:
            cursor = conexion.cursor()
            # Preparar datos para actualizar, serializando 'productos' si está presente
            datos_actualizar = nuevos_datos.copy()
            if 'productos' in datos_actualizar:
                datos_actualizar['productos'] = json.dumps(datos_actualizar['productos'])

            set_clause = ", ".join([f"{clave} = ?" for clave in datos_actualizar])
            valores = list(datos_actualizar.values())
            valores.append(id_transaccion)

            cursor.execute(f"UPDATE Transacciones SET {set_clause} WHERE id_transaccion = ?", valores)
            if cursor.rowcount == 0:
                print(f"Advertencia: Transacción ID {id_transaccion} no encontrada en la BD al intentar actualizar.")
                return False
            conexion.commit()
            print(f"Transacción ID {id_transaccion} actualizada en la BD.")
            return True
        except sqlite3.Error as e:
            print(f"Error al actualizar transacción ID {id_transaccion} en la BD: {e}")
            if conexion: conexion.rollback()
            return False
        except json.JSONDecodeError as je:
             print(f"Error al serializar productos para actualizar transacción ID {id_transaccion}: {je}")
             if conexion: conexion.rollback()
             return False
        finally:
            if conexion: conexion.close()

    def eliminar_transaccion(self, id_transaccion):
        # Elimina de BD
        conexion = conectar_db()
        if not conexion: return False
        eliminado_db = False
        try:
            cursor = conexion.cursor()
            cursor.execute("PRAGMA foreign_keys = ON") # Para borrado en cascada de Movimientos
            cursor.execute("DELETE FROM Transacciones WHERE id_transaccion = ?", (id_transaccion,))
            if cursor.rowcount > 0:
                conexion.commit()
                eliminado_db = True
                print(f"Transacción ID {id_transaccion} eliminada de la BD (y movimientos asociados).")
            else:
                print(f"Advertencia: Transacción ID {id_transaccion} no encontrada en la BD.")
        except sqlite3.Error as e:
            print(f"Error al eliminar transacción ID {id_transaccion} de la BD: {e}")
            if conexion: conexion.rollback()
            return False
        finally:
            if conexion: conexion.close()

        # Elimina de la lista
        nodo_actual = self.raiz
        while nodo_actual:
            if nodo_actual.transaccion.id_transaccion == id_transaccion:
                if nodo_actual.anterior:
                    nodo_actual.anterior.siguiente = nodo_actual.siguiente
                else: # Es el nodo raíz
                    self.raiz = nodo_actual.siguiente
                if nodo_actual.siguiente:
                    nodo_actual.siguiente.anterior = nodo_actual.anterior
                print(f"Transacción ID {id_transaccion} eliminada de la lista.")
                return True
            nodo_actual = nodo_actual.siguiente

        if eliminado_db and not nodo_actual:
            print(f"Advertencia: Transacción ID {id_transaccion} eliminada de BD pero no encontrada en lista. Sincronizando desde BD...")
            self._cargar_desde_db()
            return True
        else:
             print(f"Error: Transacción ID {id_transaccion} no encontrada ni en BD ni en lista.")
             return False

    def consultar_transacciones(self, id_cliente=None, fecha=None):
        # Busca transacciones por ID de cliente o fecha
        nodo_actual = self.raiz
        resultados = []
        while nodo_actual:
            t = nodo_actual.transaccion
            # Filtra si se proporcionan criterios
            if (id_cliente is None or t.id_cliente == id_cliente) and \
               (fecha is None or t.fecha == fecha):
                resultados.append(t)
            nodo_actual = nodo_actual.siguiente
        return resultados