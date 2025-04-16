class Nodo:
    def __init__(self, proveedor):
        self.proveedor = proveedor
        self.anterior = None
        self.siguiente = None


class Proveedor:
    def __init__(self, id_proveedor, nombre, contacto, direccion):
        self.id_proveedor = id_proveedor
        self.nombre = nombre
        self.contacto = contacto
        self.direccion = direccion


class ListaProveedores:
    def __init__(self):
        self.raiz = None

    def registrar_proveedor(self, id_proveedor, nombre, contacto, direccion):
        proveedor = Proveedor(id_proveedor, nombre, contacto, direccion)
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

    def nodo_actualizar_proveedor(self, id_proveedor, nuevos_datos):
        if self.raiz is None:
            return False

        nodo_actual = self.raiz
        while nodo_actual:
            if nodo_actual.proveedor.id_proveedor == id_proveedor:
                for clave, valor in nuevos_datos.items():
                    setattr(nodo_actual.proveedor, clave, valor)
                return True
            nodo_actual = nodo_actual.siguiente

        return False

    def eliminar_proveedor(self, id_proveedor):
        if self.raiz is None:
            return False

        nodo_actual = self.raiz
        while nodo_actual:
            if nodo_actual.proveedor.id_proveedor == id_proveedor:
                if nodo_actual.anterior is None:
                    self.raiz = nodo_actual.siguiente
                    if self.raiz:
                        self.raiz.anterior = None
                else:
                    nodo_actual.anterior.siguiente = nodo_actual.siguiente
                    if nodo_actual.siguiente:
                        nodo_actual.siguiente.anterior = nodo_actual.anterior
                return True
            nodo_actual = nodo_actual.siguiente

        return False

    def consultar_proveedor(self, id_proveedor):
        if self.raiz is None:
            return None

        nodo_actual = self.raiz
        while nodo_actual:
            if nodo_actual.proveedor.id_proveedor == id_proveedor:
                return nodo_actual.proveedor
            nodo_actual = nodo_actual.siguiente

        return None
