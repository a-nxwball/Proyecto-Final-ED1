from datetime import date
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

class Movimiento:
    # Representa un movimiento de inventario (compra/venta) asociado a una transacción
    def __init__(self, id_estado, id_transaccion, fecha, tipo):
        self.id_estado = id_estado # ID único del movimiento
        self.id_transaccion = id_transaccion # ID de la transacción relacionada
        self.fecha = fecha # Fecha del movimiento
        self.tipo = tipo # Tipo de movimiento ('compra' o 'venta')

class NodoMovimiento:
    # Nodo para la lista doblemente enlazada de movimientos
    def __init__(self, movimiento):
        self.movimiento = movimiento
        self.anterior = None
        self.siguiente = None

class ListaMovimientos:
    def __init__(self):
        self.raiz = None
        self._cargar_desde_db()

    def _cargar_desde_db(self):
        self.raiz = None
        conexion = conectar_db()
        if not conexion: return
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM Movimientos")
            filas = cursor.fetchall()
            for fila in filas:
                movimiento = Movimiento(
                    id_estado=fila[0], id_transaccion=fila[1], fecha=fila[2], tipo=fila[3]
                )
                self._agregar_nodo(movimiento)
        except sqlite3.Error as e:
            print(f"Error al cargar movimientos desde la BD: {e}")
        finally:
            if conexion: conexion.close()

    def _agregar_nodo(self, movimiento):
        nuevo_nodo = NodoMovimiento(movimiento)
        if self.raiz is None:
            self.raiz = nuevo_nodo
        else:
            nodo_actual = self.raiz
            while nodo_actual.siguiente:
                nodo_actual = nodo_actual.siguiente
            nodo_actual.siguiente = nuevo_nodo
            nuevo_nodo.anterior = nodo_actual
        return nuevo_nodo

    def registrar_movimiento(self, id_transaccion, fecha, tipo):
        # Cambiado para aceptar atributos
        conexion = conectar_db()
        if not conexion: return None
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO Movimientos (id_transaccion, fecha, tipo)
                VALUES (?, ?, ?)
            """, (id_transaccion, fecha, tipo))
            id_estado = cursor.lastrowid
            conexion.commit()

            movimiento = Movimiento(id_estado, id_transaccion, fecha, tipo)
            nuevo_nodo = self._agregar_nodo(movimiento)
            print(f"Movimiento registrado con ID: {id_estado} para transacción ID: {id_transaccion}")
            return nuevo_nodo.movimiento
        except sqlite3.Error as e:
            # Podría fallar si id_transaccion no existe (FOREIGN KEY constraint)
            print(f"Error al registrar movimiento en la BD: {e}")
            if conexion: conexion.rollback()
            return None
        finally:
            if conexion: conexion.close()

    def consultar_movimientos(self, fecha_consulta=None, tipo_consulta=None):
        # Busca movimientos por fecha o tipo
        resultados = []
        nodo_actual = self.raiz
        while nodo_actual:
            m = nodo_actual.movimiento
            fecha_coincide = True
            tipo_coincide = True

            if fecha_consulta:
                # Asegurarse de que ambas sean objetos date para comparar
                fecha_movimiento = m.fecha
                if isinstance(fecha_movimiento, str):
                    try:
                        fecha_movimiento = date.fromisoformat(fecha_movimiento)
                    except ValueError:
                         fecha_coincide = False # No se puede comparar si el formato es inválido

                if isinstance(fecha_consulta, str):
                     try:
                         fecha_consulta_obj = date.fromisoformat(fecha_consulta)
                     except ValueError:
                          raise ValueError("Formato de fecha de consulta inválido.")
                elif isinstance(fecha_consulta, date):
                     fecha_consulta_obj = fecha_consulta
                else:
                     raise TypeError("Tipo de fecha de consulta no soportado.")

                if fecha_coincide: # Solo comparar si la fecha del movimiento es válida
                    fecha_coincide = (fecha_movimiento == fecha_consulta_obj)

            if tipo_consulta:
                tipo_coincide = (m.tipo.lower() == tipo_consulta.lower())

            if fecha_coincide and tipo_coincide:
                resultados.append(m)

            nodo_actual = nodo_actual.siguiente
        return resultados

    def consultar_movimiento_por_id_transaccion(self, id_transaccion):
         # Busca un movimiento por el ID de la transacción asociada
         nodo_actual = self.raiz
         while nodo_actual:
             if nodo_actual.movimiento.id_transaccion == id_transaccion:
                 return nodo_actual.movimiento
             nodo_actual = nodo_actual.siguiente
         return None

    def eliminar_movimiento_por_id_transaccion(self, id_transaccion):
        # Elimina de BD primero (si existe)
        conexion = conectar_db()
        if not conexion: return False
        eliminado_db = False
        try:
            cursor = conexion.cursor()
            # No necesita PRAGMA foreign_keys aquí, solo elimina el movimiento
            cursor.execute("DELETE FROM Movimientos WHERE id_transaccion = ?", (id_transaccion,))
            if cursor.rowcount > 0:
                conexion.commit()
                eliminado_db = True
                print(f"Movimiento(s) asociado(s) a transacción {id_transaccion} eliminado(s) de la BD.")
            else:
                # No es necesariamente un error, puede que no existiera movimiento para esa transacción
                print(f"Info: No se encontraron movimientos en BD para transacción {id_transaccion}.")
        except sqlite3.Error as e:
            print(f"Error al eliminar movimiento(s) para transacción {id_transaccion} de la BD: {e}")
            if conexion: conexion.rollback()
            # Decidir si continuar para eliminar de la lista o no. Mejor no continuar si BD falla.
            return False
        finally:
            if conexion: conexion.close()

        # Elimina de la lista enlazada (puede haber múltiples si no hay constraint UNIQUE(id_transaccion))
        eliminado_lista = False
        nodo_actual = self.raiz
        while nodo_actual:
            siguiente_nodo = nodo_actual.siguiente # Guardar el siguiente antes de posible eliminación
            if nodo_actual.movimiento.id_transaccion == id_transaccion:
                if nodo_actual.anterior:
                    nodo_actual.anterior.siguiente = nodo_actual.siguiente
                else: # Es el nodo raíz
                    self.raiz = nodo_actual.siguiente
                if nodo_actual.siguiente:
                    nodo_actual.siguiente.anterior = nodo_actual.anterior
                print(f"Movimiento (ID Estado: {nodo_actual.movimiento.id_estado}) eliminado de la lista.")
                eliminado_lista = True
                # No hacer break, puede haber más movimientos para la misma transacción
            nodo_actual = siguiente_nodo # Moverse al siguiente nodo guardado

        if not eliminado_lista and eliminado_db:
            print(f"Advertencia: Movimiento(s) para transacción {id_transaccion} eliminado(s) de BD pero no encontrado(s) en lista. Sincronizando desde BD...")
            self._cargar_desde_db()
            return True # Éxito porque se eliminó de BD
        elif not eliminado_lista and not eliminado_db:
             print(f"Info: No se encontraron movimientos para transacción {id_transaccion} ni en BD ni en lista.")
             return False # No se encontró nada que eliminar
        elif eliminado_lista:
             return True # Éxito, se eliminó de la lista (y se intentó en BD)
        else:
             return False # Caso inesperado
