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
    # Modelo de movimiento de inventario
    def __init__(self, id_estado, id_transaccion, fecha, tipo):
        self.id_estado = id_estado
        self.id_transaccion = id_transaccion
        self.fecha = fecha
        self.tipo = tipo

class NodoMovimiento:
    # Nodo de lista doblemente enlazada para movimientos
    def __init__(self, movimiento):
        self.movimiento = movimiento
        self.anterior = None
        self.siguiente = None

class ListaMovimientos:
    # Lista doblemente enlazada de movimientos con sincronización a BD
    def __init__(self):
        self.raiz = None
        self._cargar_desde_db()

    def _cargar_desde_db(self):
        # Carga movimientos desde la base de datos
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
            pass
        finally:
            if conexion: conexion.close()

    def _agregar_nodo(self, movimiento):
        # Agrega un nodo a la lista
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
        # Registra un movimiento en la BD y la lista
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
            if conexion: conexion.rollback()
            return None
        finally:
            if conexion: conexion.close()

    def resumen_movimientos_por_rango(self, fecha_inicio, fecha_fin, tipo=None):
        # Resumen de movimientos entre dos fechas y tipo
        from datetime import date
        def parse_fecha(f):
            if isinstance(f, date):
                return f
            return date.fromisoformat(f)
        fecha_inicio = parse_fecha(fecha_inicio)
        fecha_fin = parse_fecha(fecha_fin)
        resultados = []
        nodo_actual = self.raiz
        while nodo_actual:
            m = nodo_actual.movimiento
            try:
                fecha_mov = parse_fecha(m.fecha)
            except Exception:
                nodo_actual = nodo_actual.siguiente
                continue
            if fecha_inicio <= fecha_mov <= fecha_fin:
                if tipo is None or m.tipo.lower() == tipo.lower():
                    resultados.append(m)
            nodo_actual = nodo_actual.siguiente
        resumen = {
            "total_movimientos": len(resultados),
            "movimientos": resultados
        }
        return resumen

    def consultar_movimientos(self, fecha_consulta=None, tipo_consulta=None):
        # Consulta movimientos por fecha, tipo o ambos
        from datetime import date, timedelta
        if fecha_consulta:
            fecha_inicio = fecha_fin = fecha_consulta
        else:
            fecha_inicio = "1900-01-01"
            fecha_fin = "2999-12-31"
        resumen = self.resumen_movimientos_por_rango(fecha_inicio, fecha_fin, tipo_consulta)
        return resumen["movimientos"]

    def consultar_movimiento_por_id_transaccion(self, id_transaccion):
        # Busca un movimiento por ID de transacción
        nodo_actual = self.raiz
        while nodo_actual:
            if nodo_actual.movimiento.id_transaccion == id_transaccion:
                return nodo_actual.movimiento
            nodo_actual = nodo_actual.siguiente
        return None

    def eliminar_movimiento_por_id_transaccion(self, id_transaccion):
        # Elimina un movimiento de la BD y la lista por ID de transacción
        conexion = conectar_db()
        if not conexion: return False
        eliminado_db = False
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM Movimientos WHERE id_transaccion = ?", (id_transaccion,))
            if cursor.rowcount > 0:
                conexion.commit()
                eliminado_db = True
                print(f"Movimiento(s) asociado(s) a transacción {id_transaccion} eliminado(s) de la BD.")
        except sqlite3.Error as e:
            if conexion: conexion.rollback()
            return False
        finally:
            if conexion: conexion.close()

        eliminado_lista = False
        nodo_actual = self.raiz
        while nodo_actual:
            siguiente_nodo = nodo_actual.siguiente
            if nodo_actual.movimiento.id_transaccion == id_transaccion:
                if nodo_actual.anterior:
                    nodo_actual.anterior.siguiente = nodo_actual.siguiente
                else:
                    self.raiz = nodo_actual.siguiente
                if nodo_actual.siguiente:
                    nodo_actual.siguiente.anterior = nodo_actual.anterior
                print(f"Movimiento (ID Estado: {nodo_actual.movimiento.id_estado}) eliminado de la lista.")
                eliminado_lista = True
            nodo_actual = siguiente_nodo

        if not eliminado_lista and eliminado_db:
            self._cargar_desde_db()
            return True
        elif not eliminado_lista and not eliminado_db:
            return False
        elif eliminado_lista:
            return True
        else:
            return False

    def reporte_logistico_final(self, lista_productos, fecha_inicio=None, fecha_fin=None, id_producto=None):
        """
        Reporte logístico avanzado: muestra movimientos físicos (entradas, salidas, stock inicial/final),
        permite filtrar por producto y fechas. Incluye rotación, productos más/menos movidos y alertas de stock mínimo.
        """
        from collections import defaultdict
        from datetime import date as dtdate

        def parse_fecha(f):
            if isinstance(f, dtdate):
                return f
            return dtdate.fromisoformat(f)

        # Filtrar movimientos por fecha y producto
        movimientos_filtrados = []
        nodo = self.raiz
        while nodo:
            m = nodo.movimiento
            cumple_fecha = True
            if fecha_inicio and fecha_fin:
                try:
                    fecha_mov = parse_fecha(m.fecha)
                    cumple_fecha = (fecha_mov >= parse_fecha(fecha_inicio) and fecha_mov <= parse_fecha(fecha_fin))
                except Exception:
                    cumple_fecha = False
            if cumple_fecha:
                movimientos_filtrados.append(m)
            nodo = nodo.siguiente

        # Agrupar por producto
        rotacion = defaultdict(int)
        entradas = defaultdict(int)
        salidas = defaultdict(int)
        stock_inicial = {}
        stock_final = {}

        # Obtener stock inicial/final y rotación
        productos = lista_productos.consultar_producto()
        for p in productos:
            stock_inicial[p.id_producto] = p.stock
            stock_final[p.id_producto] = p.stock

        for m in movimientos_filtrados:
            # Buscar productos involucrados en la transacción
            # Se asume que la transacción tiene productos como lista de IDs o dicts
            from app.ModuloTransacciones import ListaTransacciones
            transacciones = ListaTransacciones()
            t = None
            nodo_t = transacciones.raiz
            while nodo_t:
                if nodo_t.transaccion.id_transaccion == m.id_transaccion:
                    t = nodo_t.transaccion
                    break
                nodo_t = nodo_t.siguiente
            if not t:
                continue
            productos_ids = []
            if isinstance(t.productos, list):
                for x in t.productos:
                    if isinstance(x, dict):
                        productos_ids.append(x.get("id"))
                    else:
                        productos_ids.append(x)
            else:
                try:
                    productos_ids = [int(t.productos)]
                except Exception:
                    continue
            for pid in productos_ids:
                if id_producto and pid != id_producto:
                    continue
                rotacion[pid] += 1
                if m.tipo.lower() == "compra":
                    entradas[pid] += 1
                elif m.tipo.lower() == "venta":
                    salidas[pid] += 1

        # Productos más y menos movidos
        if rotacion:
            max_rot = max(rotacion.values())
            min_rot = min(rotacion.values())
            productos_mas_movidos = [pid for pid, v in rotacion.items() if v == max_rot]
            productos_menos_movidos = [pid for pid, v in rotacion.items() if v == min_rot]
        else:
            productos_mas_movidos = []
            productos_menos_movidos = []

        # Alertas por stock mínimo
        alertas_stock = []
        for p in productos:
            if p.stock <= 5:
                alertas_stock.append(f"⚠️ Stock mínimo para producto {p.nombre} (ID {p.id_producto}): {p.stock}")

        print("\n===== REPORTE LOGÍSTICO FINAL =====")
        if fecha_inicio and fecha_fin:
            print(f"Rango de fechas: {fecha_inicio} a {fecha_fin}")
        if id_producto:
            print(f"Producto ID: {id_producto}")
        print("-----------------------------------")
        print("Rotación de productos (movimientos):")
        for pid, v in rotacion.items():
            nombre = next((p.nombre for p in productos if p.id_producto == pid), str(pid))
            print(f"Producto {nombre} (ID {pid}): {v} movimientos")
        print("-----------------------------------")
        print("Entradas por producto:")
        for pid, v in entradas.items():
            nombre = next((p.nombre for p in productos if p.id_producto == pid), str(pid))
            print(f"Producto {nombre} (ID {pid}): {v} entradas")
        print("Salidas por producto:")
        for pid, v in salidas.items():
            nombre = next((p.nombre for p in productos if p.id_producto == pid), str(pid))
            print(f"Producto {nombre} (ID {pid}): {v} salidas")
        print("-----------------------------------")
        print("Productos más movidos:", productos_mas_movidos)
        print("Productos menos movidos:", productos_menos_movidos)
        print("-----------------------------------")
        print("Alertas de stock mínimo:")
        for alerta in alertas_stock:
            print(alerta)
        print("===== FIN REPORTE LOGÍSTICO =====\n")
        return {
            "rotacion": dict(rotacion),
            "entradas": dict(entradas),
            "salidas": dict(salidas),
            "productos_mas_movidos": productos_mas_movidos,
            "productos_menos_movidos": productos_menos_movidos,
            "alertas_stock": alertas_stock
        }
