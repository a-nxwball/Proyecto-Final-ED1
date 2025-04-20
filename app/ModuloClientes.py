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

class Cliente:
    def __init__(self, id_cliente, nombre, contacto, direccion, tipo_cliente, credito=0):
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.contacto = contacto
        self.direccion = direccion
        self.tipo_cliente = tipo_cliente
        self.credito = credito

class NodoCliente:
    def __init__(self, cliente):
        self.cliente = cliente
        self.anterior = None
        self.siguiente = None

class ListaClientes:
    def __init__(self):
        self.raiz = None
        self._cargar_desde_db()

    def _cargar_desde_db(self):
        self.raiz = None
        conexion = conectar_db()
        if not conexion: return
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM Clientes")
            filas = cursor.fetchall()
            for fila in filas:
                cliente = Cliente(
                    id_cliente=fila[0], nombre=fila[1], contacto=fila[2],
                    direccion=fila[3], tipo_cliente=fila[4], credito=fila[5]
                )
                self._agregar_nodo(cliente)
        except sqlite3.Error as e:
            print(f"Error al cargar clientes desde la BD: {e}")
        finally:
            if conexion: conexion.close()

    def _agregar_nodo(self, cliente):
        nuevo_nodo = NodoCliente(cliente)
        if self.raiz is None:
            self.raiz = nuevo_nodo
        else:
            nodo_actual = self.raiz
            while nodo_actual.siguiente:
                nodo_actual = nodo_actual.siguiente
            nodo_actual.siguiente = nuevo_nodo
            nuevo_nodo.anterior = nodo_actual
        return nuevo_nodo

    def registrar_cliente(self, nombre, contacto, direccion, tipo_cliente, credito=0):
        conexion = conectar_db()
        if not conexion: return None
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO Clientes (nombre, contacto, direccion, tipo_cliente, credito)
                VALUES (?, ?, ?, ?, ?)
            """, (nombre, contacto, direccion, tipo_cliente, credito))
            id_cliente = cursor.lastrowid
            conexion.commit()
            cliente = Cliente(id_cliente, nombre, contacto, direccion, tipo_cliente, credito)
            nuevo_nodo = self._agregar_nodo(cliente)
            print(f"Cliente '{nombre}' registrado con ID: {id_cliente}")
            return nuevo_nodo.cliente
        except sqlite3.Error as e:
            print(f"Error al registrar cliente en la BD: {e}")
            if conexion: conexion.rollback()
            return None
        finally:
            if conexion: conexion.close()

    def actualizar_cliente(self, id_cliente, nuevos_datos):
        nodo_actual = self.raiz
        cliente_encontrado = None
        while nodo_actual:
            if nodo_actual.cliente.id_cliente == id_cliente:
                cliente_encontrado = nodo_actual.cliente
                for clave, valor in nuevos_datos.items():
                    setattr(cliente_encontrado, clave, valor)
                break
            nodo_actual = nodo_actual.siguiente

        if not cliente_encontrado:
            print(f"Error: Cliente ID {id_cliente} no encontrado en lista. Sincronizando desde BD...")
            self._cargar_desde_db()
            return False

        conexion = conectar_db()
        if not conexion: return False
        try:
            cursor = conexion.cursor()
            set_clause = ", ".join([f"{clave} = ?" for clave in nuevos_datos])
            valores = list(nuevos_datos.values())
            valores.append(id_cliente)
            cursor.execute(f"UPDATE Clientes SET {set_clause} WHERE id_cliente = ?", valores)
            if cursor.rowcount == 0:
                print(f"Advertencia: Cliente ID {id_cliente} no encontrado en la BD al intentar actualizar.")
                return False
            conexion.commit()
            print(f"Cliente ID {id_cliente} actualizado en la BD.")
            return True
        except sqlite3.Error as e:
            print(f"Error al actualizar cliente ID {id_cliente} en la BD: {e}")
            if conexion: conexion.rollback()
            return False
        finally:
            if conexion: conexion.close()

    def eliminar_cliente(self, id_cliente):
        conexion = conectar_db()
        if not conexion: return False
        eliminado_db = False
        try:
            cursor = conexion.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("DELETE FROM Clientes WHERE id_cliente = ?", (id_cliente,))
            if cursor.rowcount > 0:
                conexion.commit()
                eliminado_db = True
                print(f"Cliente ID {id_cliente} eliminado de la BD (y transacciones/movimientos asociados si existen).")
            else:
                print(f"Advertencia: Cliente ID {id_cliente} no encontrado en la BD.")
        except sqlite3.Error as e:
            print(f"Error al eliminar cliente ID {id_cliente} de la BD: {e}")
            if conexion: conexion.rollback()
            return False
        finally:
            if conexion: conexion.close()

        nodo_actual = self.raiz
        while nodo_actual:
            if nodo_actual.cliente.id_cliente == id_cliente:
                if nodo_actual.anterior:
                    nodo_actual.anterior.siguiente = nodo_actual.siguiente
                else:
                    self.raiz = nodo_actual.siguiente
                if nodo_actual.siguiente:
                    nodo_actual.siguiente.anterior = nodo_actual.anterior
                print(f"Cliente ID {id_cliente} eliminado de la lista.")
                return True
            nodo_actual = nodo_actual.siguiente

        if eliminado_db and not nodo_actual:
            print(f"Advertencia: Cliente ID {id_cliente} eliminado de BD pero no encontrado en lista. Sincronizando desde BD...")
            self._cargar_desde_db()
            return True
        else:
             print(f"Error: Cliente ID {id_cliente} no encontrado ni en BD ni en lista.")
             return False

    def consultar_cliente(self, id_cliente=None, nombre=None):
        nodo_actual = self.raiz
        resultados = []
        while nodo_actual:
            c = nodo_actual.cliente
            if (id_cliente is None or c.id_cliente == id_cliente) and (nombre is None or c.nombre.lower() == nombre.lower()):
                resultados.append(c)
            nodo_actual = nodo_actual.siguiente
        
        return resultados

    def resumen_movimientos_cliente(self, movimientos_lista, id_cliente, fecha_inicio, fecha_fin, tipo=None):
        """
        Devuelve un resumen de movimientos de un cliente específico en un rango de fechas y por tipo.
        movimientos_lista: instancia de ListaMovimientos.
        """
        if not movimientos_lista:
            print("Debe proporcionar una instancia de ListaMovimientos.")
            return None
        from app.ModuloTransacciones import ListaTransacciones
        transacciones = ListaTransacciones()
        transacciones_cliente = []
        nodo = transacciones.raiz
        while nodo:
            if nodo.transaccion.id_cliente == id_cliente:
                transacciones_cliente.append(nodo.transaccion.id_transaccion)
            nodo = nodo.siguiente
        resumen = movimientos_lista.resumen_movimientos_por_rango(fecha_inicio, fecha_fin, tipo)
        movimientos_filtrados = [
            m for m in resumen["movimientos"] if m.id_transaccion in transacciones_cliente
        ]
        return {
            "total_movimientos": len(movimientos_filtrados),
            "movimientos": movimientos_filtrados
        }