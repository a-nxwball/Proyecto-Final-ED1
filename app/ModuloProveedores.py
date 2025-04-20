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

class Nodo:
    # Nodo para la lista doblemente enlazada de proveedores
    def __init__(self, proveedor):
        self.proveedor = proveedor
        self.anterior = None
        self.siguiente = None

class Proveedor:
    # Representa un proveedor
    def __init__(self, id_proveedor, nombre, contacto, direccion):
        self.id_proveedor = id_proveedor
        self.nombre = nombre
        self.contacto = contacto
        self.direccion = direccion

class ListaProveedores:
    def __init__(self):
        self.raiz = None
        self._cargar_desde_db()

    def _cargar_desde_db(self):
        self.raiz = None
        conexion = conectar_db()
        if not conexion: return
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM Proveedores")
            filas = cursor.fetchall()
            for fila in filas:
                proveedor = Proveedor(id_proveedor=fila[0], nombre=fila[1], contacto=fila[2], direccion=fila[3])
                self._agregar_nodo(proveedor)
        except sqlite3.Error as e:
            print(f"Error al cargar proveedores desde la BD: {e}")
        finally:
            if conexion: conexion.close()

    def _agregar_nodo(self, proveedor):
        nuevo_nodo = Nodo(proveedor)
        if self.raiz is None:
            self.raiz = nuevo_nodo
        else:
            nodo_actual = self.raiz
            while nodo_actual.siguiente:
                nodo_actual = nodo_actual.siguiente
            nodo_actual.siguiente = nuevo_nodo
            nuevo_nodo.anterior = nodo_actual
        return nuevo_nodo

    def registrar_proveedor(self, nombre, contacto, direccion):
        conexion = conectar_db()
        if not conexion: return None
        try:
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO Proveedores (nombre, contacto, direccion) VALUES (?, ?, ?)",
                           (nombre, contacto, direccion))
            id_proveedor = cursor.lastrowid
            conexion.commit()
            proveedor = Proveedor(id_proveedor, nombre, contacto, direccion)
            nuevo_nodo = self._agregar_nodo(proveedor)
            print(f"Proveedor '{nombre}' registrado con ID: {id_proveedor}")
            return nuevo_nodo.proveedor
        except sqlite3.Error as e:
            print(f"Error al registrar proveedor en la BD: {e}")
            if conexion: conexion.rollback()
            return None
        finally:
            if conexion: conexion.close()

    def actualizar_proveedor(self, id_proveedor, nuevos_datos):
        # Actualiza en memoria
        nodo_actual = self.raiz
        proveedor_encontrado = None
        while nodo_actual:
            if nodo_actual.proveedor.id_proveedor == id_proveedor:
                proveedor_encontrado = nodo_actual.proveedor
                for clave, valor in nuevos_datos.items():
                    setattr(proveedor_encontrado, clave, valor)
                break
            nodo_actual = nodo_actual.siguiente

        if not proveedor_encontrado:
            print(f"Error: Proveedor ID {id_proveedor} no encontrado en lista. Sincronizando desde BD...")
            self._cargar_desde_db()
            return False

        # Actualiza en BD
        conexion = conectar_db()
        if not conexion: return False
        try:
            cursor = conexion.cursor()
            set_clause = ", ".join([f"{clave} = ?" for clave in nuevos_datos])
            valores = list(nuevos_datos.values())
            valores.append(id_proveedor)
            cursor.execute(f"UPDATE Proveedores SET {set_clause} WHERE id_proveedor = ?", valores)
            if cursor.rowcount == 0:
                print(f"Advertencia: Proveedor ID {id_proveedor} no encontrado en la BD al intentar actualizar.")
                return False
            conexion.commit()
            print(f"Proveedor ID {id_proveedor} actualizado en la BD.")
            return True
        except sqlite3.Error as e:
            print(f"Error al actualizar proveedor ID {id_proveedor} en la BD: {e}")
            if conexion: conexion.rollback()
            return False
        finally:
            if conexion: conexion.close()

    def eliminar_proveedor(self, id_proveedor):
        # Elimina de BD
        conexion = conectar_db()
        if not conexion: return False
        eliminado_db = False
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM Proveedores WHERE id_proveedor = ?", (id_proveedor,))
            if cursor.rowcount > 0:
                conexion.commit()
                eliminado_db = True
                print(f"Proveedor ID {id_proveedor} eliminado de la BD.")
            else:
                print(f"Advertencia: Proveedor ID {id_proveedor} no encontrado en la BD.")
        except sqlite3.Error as e:
            print(f"Error al eliminar proveedor ID {id_proveedor} de la BD: {e}")
            if conexion: conexion.rollback()
            return False
        finally:
            if conexion: conexion.close()

        # Elimina de la lista
        nodo_actual = self.raiz
        while nodo_actual:
            if nodo_actual.proveedor.id_proveedor == id_proveedor:
                if nodo_actual.anterior is None: # Es el nodo raíz
                    self.raiz = nodo_actual.siguiente
                    if self.raiz: self.raiz.anterior = None
                else:
                    nodo_actual.anterior.siguiente = nodo_actual.siguiente
                    if nodo_actual.siguiente: nodo_actual.siguiente.anterior = nodo_actual.anterior
                print(f"Proveedor ID {id_proveedor} eliminado de la lista.")
                return True
            nodo_actual = nodo_actual.siguiente

        if eliminado_db and not nodo_actual:
            print(f"Advertencia: Proveedor ID {id_proveedor} eliminado de BD pero no encontrado en lista. Sincronizando desde BD...")
            self._cargar_desde_db()
            return True

        if eliminado_db:
             print(f"Advertencia: Proveedor ID {id_proveedor} eliminado de BD pero no encontrado en lista.")
             return True
        else:
             print(f"Error: Proveedor ID {id_proveedor} no encontrado ni en BD ni en lista.")
             return False

    def consultar_proveedor(self, id_proveedor):
        # Busca un proveedor por su ID
        if self.raiz is None:
            return None

        nodo_actual = self.raiz
        while nodo_actual:
            if nodo_actual.proveedor.id_proveedor == id_proveedor:
                return nodo_actual.proveedor
            nodo_actual = nodo_actual.siguiente

        return None