class NodoTransaccion:
    def __init__(self, transaccion):
        self.transaccion = transaccion
        self.anterior = None
        self.siguiente = None
        
class Transaccion:
    def __init__(self, id_transaccion, id_cliente, productos, total, fecha, tipo_pago, estado):
        self.id_transaccion = id_transaccion
        self.id_cliente = id_cliente
        self.productos = productos
        self.total = total
        self.fecha = fecha
        self.tipo_pago = tipo_pago
        self.estado = estado

class ListaTransacciones:
    def __init__(self):
        self.raiz = None

    def registrar_transaccion(self, transaccion):
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

    def actualizar_transaccion(self, id_transaccion, nuevos_datos):
        nodo_actual = self.raiz
        while nodo_actual:
            if nodo_actual.transaccion.id_transaccion == id_transaccion:
                for clave, valor in nuevos_datos.items():
                    setattr(nodo_actual.transaccion, clave, valor)
                return True
            nodo_actual = nodo_actual.siguiente
        return False

    def eliminar_transaccion(self, id_transaccion):
        # Elimina la transacción identificada por su ID.
        nodo_actual = self.raiz
        while nodo_actual:
            if nodo_actual.transaccion.id_transaccion == id_transaccion:
                if nodo_actual.anterior:
                    nodo_actual.anterior.siguiente = nodo_actual.siguiente
                else:
                    self.raiz = nodo_actual.siguiente
                if nodo_actual.siguiente:
                    nodo_actual.siguiente.anterior = nodo_actual.anterior
                return True
            nodo_actual = nodo_actual.siguiente
        return False

    def consultar_transacciones(self, id_cliente=None, fecha=None):
        nodo_actual = self.raiz
        resultados = []
        while nodo_actual:
            t = nodo_actual.transaccion
            if (id_cliente is None or t.id_cliente == id_cliente) and (fecha is None or t.fecha == fecha):
                resultados.append(t)
            nodo_actual = nodo_actual.siguiente
        return resultados