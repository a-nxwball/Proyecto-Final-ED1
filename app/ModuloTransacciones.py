import sqlite3
import json
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
    # Nodo de lista doblemente enlazada para transacciones
    def __init__(self, transaccion):
        self.transaccion = transaccion
        self.anterior = None
        self.siguiente = None

class Transaccion:
    # Modelo de transacción
    def __init__(self, id_transaccion, id_cliente, id_proveedor, productos, total, fecha, tipo_pago, estado):
        self.id_transaccion = id_transaccion
        self.id_cliente = id_cliente
        self.id_proveedor = id_proveedor
        self.productos = productos
        self.total = total
        self.fecha = fecha
        self.tipo_pago = tipo_pago
        self.estado = estado

class ListaTransacciones:
    # Lista doblemente enlazada de transacciones con sincronización a BD
    def __init__(self):
        self.raiz = None
        self._cargar_desde_db()

    def _cargar_desde_db(self):
        # Carga transacciones desde la base de datos
        self.raiz = None
        conexion = conectar_db()
        if not conexion: return
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM Transacciones")
            filas = cursor.fetchall()
            for fila in filas:
                try:
                    productos_lista = json.loads(fila[3]) if fila[3] else []
                except json.JSONDecodeError:
                    productos_lista = []
                # Asegurarse de que el total sea float
                total_val = float(fila[4]) if fila[4] is not None else 0.0
                transaccion = Transaccion(
                    id_transaccion=fila[0],
                    id_cliente=fila[1],
                    id_proveedor=fila[2],
                    productos=productos_lista,
                    total=total_val,
                    fecha=fila[5],
                    tipo_pago=fila[6],
                    estado=fila[7]
                )
                self._agregar_nodo(transaccion)
        except sqlite3.Error as e:
            pass
        finally:
            if conexion: conexion.close()

    def _agregar_nodo(self, transaccion):
        # Agrega un nodo a la lista
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

    def registrar_transaccion(self, id_cliente=None, productos=None, total=0.0, fecha=None, tipo_pago=None, estado=None, id_proveedor=None):
        # Registra una transacción en la BD y la lista
        conexion = conectar_db()
        if not conexion: return None
        try:
            productos_json = json.dumps(productos) if productos is not None else "[]"
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO Transacciones (id_cliente, id_proveedor, productos, total, fecha, tipo_pago, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id_cliente, id_proveedor, productos_json, total, fecha, tipo_pago, estado))
            id_transaccion = cursor.lastrowid
            conexion.commit()
            transaccion = Transaccion(id_transaccion, id_cliente, id_proveedor, productos, total, fecha, tipo_pago, estado)
            nuevo_nodo = self._agregar_nodo(transaccion)
            print(f"Transacción registrada con ID: {id_transaccion}")
            return nuevo_nodo.transaccion
        except sqlite3.Error as e:
            if conexion: conexion.rollback()
            return None
        except json.JSONDecodeError as je:
            if conexion: conexion.rollback()
            return None
        finally:
            if conexion: conexion.close()

    def actualizar_transaccion(self, id_transaccion, nuevos_datos):
        # Actualiza una transacción en la lista y la BD
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
            self._cargar_desde_db()
            return False

        conexion = conectar_db()
        if not conexion: return False
        try:
            cursor = conexion.cursor()
            datos_actualizar = nuevos_datos.copy()
            if 'productos' in datos_actualizar:
                datos_actualizar['productos'] = json.dumps(datos_actualizar['productos'])
            set_clause = ", ".join([f"{clave} = ?" for clave in datos_actualizar])
            valores = list(datos_actualizar.values())
            valores.append(id_transaccion)
            cursor.execute(f"UPDATE Transacciones SET {set_clause} WHERE id_transaccion = ?", valores)
            if cursor.rowcount == 0:
                return False
            conexion.commit()
            print(f"Transacción ID {id_transaccion} actualizada en la BD.")
            return True
        except sqlite3.Error as e:
            if conexion: conexion.rollback()
            return False
        except json.JSONDecodeError as je:
            if conexion: conexion.rollback()
            return False
        finally:
            if conexion: conexion.close()

    def eliminar_transaccion(self, id_transaccion):
        # Elimina una transacción de la BD y la lista
        conexion = conectar_db()
        if not conexion: return False
        eliminado_db = False
        try:
            cursor = conexion.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("DELETE FROM Transacciones WHERE id_transaccion = ?", (id_transaccion,))
            if cursor.rowcount > 0:
                conexion.commit()
                eliminado_db = True
                print(f"Transacción ID {id_transaccion} eliminada de la BD (y movimientos asociados).")
        except sqlite3.Error as e:
            if conexion: conexion.rollback()
            return False
        finally:
            if conexion: conexion.close()

        nodo_actual = self.raiz
        while nodo_actual:
            if nodo_actual.transaccion.id_transaccion == id_transaccion:
                if nodo_actual.anterior:
                    nodo_actual.anterior.siguiente = nodo_actual.siguiente
                else:
                    self.raiz = nodo_actual.siguiente
                if nodo_actual.siguiente:
                    nodo_actual.siguiente.anterior = nodo_actual.anterior
                print(f"Transacción ID {id_transaccion} eliminada de la lista.")
                return True
            nodo_actual = nodo_actual.siguiente

        if eliminado_db and not nodo_actual:
            self._cargar_desde_db()
            return True
        else:
            return False

    def consultar_transacciones(self, id_cliente=None, fecha=None, id_proveedor=None):
        # Consulta transacciones por ID de cliente, proveedor o fecha
        nodo_actual = self.raiz
        resultados = []
        while nodo_actual:
            t = nodo_actual.transaccion
            if (id_cliente is None or t.id_cliente == id_cliente) and \
               (id_proveedor is None or t.id_proveedor == id_proveedor) and \
               (fecha is None or t.fecha == fecha):
                resultados.append(t)
            nodo_actual = nodo_actual.siguiente
        return resultados

    def resumen_movimientos_por_rango(self, movimientos_lista, fecha_inicio, fecha_fin, tipo=None):
        # Resumen de movimientos relacionados a las transacciones
        if not movimientos_lista:
            return None
        return movimientos_lista.resumen_movimientos_por_rango(fecha_inicio, fecha_fin, tipo)

    def reporte_transaccional_final(self, movimientos_lista, fecha_inicio=None, fecha_fin=None, id_cliente=None, id_proveedor=None):
        """
        Reporte transaccional avanzado: muestra todas las transacciones financieras (compras, ventas, pagos, deudas, utilidades),
        agrupadas por rango de fechas, cliente o proveedor.
        Incluye totales de compra, venta, utilidad bruta y neta, pagos realizados y saldos pendientes.
        """
        nodo = self.raiz
        transacciones_filtradas = []
        while nodo:
            t = nodo.transaccion
            cumple_fecha = True
            if fecha_inicio and fecha_fin:
                cumple_fecha = (t.fecha >= fecha_inicio and t.fecha <= fecha_fin)
            if (id_cliente is None or t.id_cliente == id_cliente) and \
               (id_proveedor is None or t.id_proveedor == id_proveedor) and cumple_fecha:
                transacciones_filtradas.append(t)
            nodo = nodo.siguiente

        total_ventas = 0.0
        total_compras = 0.0
        pagos_realizados = 0.0
        saldo_pendiente = 0.0
        utilidad_bruta = 0.0
        utilidad_neta = 0.0

        for t in transacciones_filtradas:
            if t.estado and t.estado.lower() == "completada":
                if t.tipo_pago and "compra" in t.tipo_pago.lower():
                    total_compras += t.total
                else:
                    total_ventas += t.total
                    if t.tipo_pago and ("efectivo" in t.tipo_pago.lower() or "tarjeta" in t.tipo_pago.lower()):
                        pagos_realizados += t.total
            elif t.estado and t.estado.lower() == "pendiente":
                saldo_pendiente += t.total

        utilidad_bruta = total_ventas - total_compras
        utilidad_neta = utilidad_bruta  # Si hay otros gastos, restar aquí

        print("\n===== REPORTE TRANSACCIONAL FINAL =====")
        if fecha_inicio and fecha_fin:
            print(f"Rango de fechas: {fecha_inicio} a {fecha_fin}")
        if id_cliente:
            print(f"Cliente ID: {id_cliente}")
        if id_proveedor:
            print(f"Proveedor ID: {id_proveedor}")
        print("---------------------------------------")
        print(f"Total de ventas: ${total_ventas:.2f}")
        print(f"Total de compras: ${total_compras:.2f}")
        print(f"Utilidad bruta: ${utilidad_bruta:.2f}")
        print(f"Utilidad neta: ${utilidad_neta:.2f}")
        print(f"Pagos realizados: ${pagos_realizados:.2f}")
        print(f"Saldos pendientes: ${saldo_pendiente:.2f}")
        print("---------------------------------------")
        print("Detalle de transacciones:")
        for t in transacciones_filtradas:
            print(vars(t))
        print("===== FIN REPORTE TRANSACCIONAL =====\n")
        return {
            "ventas": total_ventas,
            "compras": total_compras,
            "utilidad_bruta": utilidad_bruta,
            "utilidad_neta": utilidad_neta,
            "pagos_realizados": pagos_realizados,
            "saldo_pendiente": saldo_pendiente,
            "transacciones": transacciones_filtradas
        }