from datetime import date, timedelta

class Producto:
    """Representa un producto en el inventario."""
    def __init__(self, id_producto, nombre, descripcion, categoria, precio, stock, fecha_expiracion=None, temporalidad=False, rebaja=0.0):
        self.id_producto = id_producto
        self.nombre = nombre
        self.descripcion = descripcion
        self.categoria = categoria
        self.precio = precio
        self.stock = stock
        self.fecha_expiracion = fecha_expiracion  # Puede ser None si no aplica
        self.temporalidad = temporalidad
        self.rebaja = rebaja  # Porcentaje de rebaja (ej. 0.1 para 10%)

class NodoProducto:
    """Nodo para la lista doblemente enlazada de productos."""
    def __init__(self, producto):
        self.producto = producto
        self.anterior = None
        self.siguiente = None

class ListaProductos:
    """Gestiona la lista doblemente enlazada de productos."""
    def __init__(self):
        self.raiz = None

    def registrar_producto(self, producto):
        """Registra un nuevo producto en la lista."""
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

    def actualizar_producto(self, id_producto, nuevos_datos):
        """Actualiza la información de un producto existente por su ID."""
        nodo_actual = self.raiz
        while nodo_actual:
            if nodo_actual.producto.id_producto == id_producto:
                for clave, valor in nuevos_datos.items():
                    # Validar que el atributo exista antes de asignarlo
                    if hasattr(nodo_actual.producto, clave):
                        setattr(nodo_actual.producto, clave, valor)
                    else:
                        print(f"Advertencia: El atributo '{clave}' no existe en Producto.")
                return True
            nodo_actual = nodo_actual.siguiente
        return False # Producto no encontrado

    def eliminar_producto(self, id_producto):
        """Elimina un producto de la lista por su ID."""
        nodo_actual = self.raiz
        while nodo_actual:
            if nodo_actual.producto.id_producto == id_producto:
                if nodo_actual.anterior:
                    nodo_actual.anterior.siguiente = nodo_actual.siguiente
                else: # Es el nodo raíz
                    self.raiz = nodo_actual.siguiente
                if nodo_actual.siguiente:
                    nodo_actual.siguiente.anterior = nodo_actual.anterior
                # Opcional: liberar memoria (en Python no es estrictamente necesario)
                # del nodo_actual
                return True # Producto eliminado
            nodo_actual = nodo_actual.siguiente
        return False # Producto no encontrado

    def consultar_producto(self, id_producto=None, nombre=None):
        """Consulta productos por ID o nombre. Devuelve una lista de productos."""
        resultados = []
        nodo_actual = self.raiz
        while nodo_actual:
            p = nodo_actual.producto
            # Comprobar si coincide el ID (si se proporciona)
            id_coincide = (id_producto is None or p.id_producto == id_producto)
            # Comprobar si coincide el nombre (insensible a mayúsculas/minúsculas, si se proporciona)
            nombre_coincide = (nombre is None or p.nombre.lower() == nombre.lower())

            if id_coincide and nombre_coincide:
                resultados.append(p)
            
            # Si buscamos por ID único y ya lo encontramos, podemos parar
            if id_producto is not None and id_coincide:
                break
                
            nodo_actual = nodo_actual.siguiente
        return resultados
