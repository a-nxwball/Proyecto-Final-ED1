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

    def registrar_cliente(self, cliente):
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

    def actualizar_cliente(self, id_cliente, nuevos_datos):
        nodo_actual = self.raiz
        while nodo_actual:
            if nodo_actual.cliente.id_cliente == id_cliente:
                for clave, valor in nuevos_datos.items():
                    setattr(nodo_actual.cliente, clave, valor)
                return True
            nodo_actual = nodo_actual.siguiente
        return False

    def eliminar_cliente(self, id_cliente):
        nodo_actual = self.raiz
        while nodo_actual:
            if nodo_actual.cliente.id_cliente == id_cliente:
                if nodo_actual.anterior:
                    nodo_actual.anterior.siguiente = nodo_actual.siguiente
                else:
                    self.raiz = nodo_actual.siguiente
                if nodo_actual.siguiente:
                    nodo_actual.siguiente.anterior = nodo_actual.anterior
                return True
            nodo_actual = nodo_actual.siguiente
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