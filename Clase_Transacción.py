""" 
    Módulo de Gestión de Transacciones:
    El módulo representa las ventas y/o transacciones realizadas a los clientes.

    - Registro de Transacciones:
        Las ventas se registran mediante la clase ListaTransacción. Cada transacción está asociada a un cliente y se almacenan los productos vendidos, el total de la venta, la fecha y los detalles de pago. Las transacciones pueden ser consultadas por fecha o por cliente (Clase EstadoMovimiento), lo que permite tener un control eficiente de ventas.

    - Aporta las propiedades de una lista doblemente enlazada para almacenar las transacciones de forma eficiente. Luego esta informacion puede ser almacenada en una base de datos o archivo para su persistencia.
    
    - Permite realizar operaciones CRUD (Crear, Leer, Actualizar, Eliminar) sobre las transacciones.

    Atributos:
    id_transaccion: ID único de la transacción.
    id_cliente: ID del cliente que realiza la compra.
    productos: Lista de productos comprados.
    total: Total de la transacción.
    fecha: Fecha de la transacción.
    tipo_pago: Método de pago (efectivo, tarjeta, crédito).
    estado: Estado de la transacción (pendiente, completada, cancelada).

    Funciones:
    registrar_transaccion(): Registra una venta realizada.
    actualizar_transaccion(): Actualiza la información de una transacción.
    eliminar_transaccion(): Elimina una transacción.
    consultar_transacciones(): Consulta las transacciones por cliente o fecha.
"""

class NodoTransaccion:
    """
    Clase que representa un nodo en la lista doblemente enlazada.

    - Cada nodo contiene una transacción y referencias al nodo anterior y siguiente.

    Atributos:
    transaccion: Transacción asociada al nodo.
    anterior: Referencia al nodo anterior en la lista.
    siguiente: Referencia al nodo siguiente en la lista.
    """
    def __init__(self, transaccion):
        self.transaccion = transaccion
        self.anterior = None
        self.siguiente = None
        
class Transaccion:
    """ 
    Clase que representa una transacción de venta.
    - Cada transacción tiene un ID único, un cliente asociado, una lista de productos vendidos, el total de la venta, la fecha y detalles de pago.
    
    Atributos:
    id_transaccion: ID único de la transacción.
    id_cliente: ID del cliente que realiza la compra.
    productos: Lista de productos comprados.
    total: Total de la transacción.
    fecha: Fecha de la transacción.
    tipo_pago: Método de pago (efectivo, tarjeta, crédito).
    estado: Estado de la transacción (pendiente, completada, cancelada).
    """
    def __init__(self, id_transaccion, id_cliente, productos, total, fecha, tipo_pago, estado):
        self.id_transaccion = id_transaccion
        self.id_cliente = id_cliente
        self.productos = productos
        self.total = total
        self.fecha = fecha
        self.tipo_pago = tipo_pago
        self.estado = estado

class ListaTransacciones:
    """
    Clase para gestionar la lista doblemente enlazada de transacciones.

    Atributos:
    raiz: Nodo inicial de la lista.

    Funciones:
    registrar_transaccion(): Registra una nueva transacción.
    actualizar_transaccion(): Actualiza una transacción existente.
    eliminar_transaccion(): Elimina una transacción por ID.
    consultar_transacciones(): Consulta transacciones por cliente o fecha.
    """
    def __init__(self):
        self.raiz = None

    def registrar_transaccion(self, transaccion):
        """
        Registra una nueva transacción en la lista doblemente enlazada.

        Parámetros:
        transaccion: Objeto Transacción a registrar.

        Retorna:
        NodoTransaccion creado.
        """
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
        """
        Actualiza la información de una transacción existente.

        Parámetros:
        id_transaccion: ID de la transacción a actualizar.
        nuevos_datos: Diccionario con los campos a actualizar.

        Retorna:
        True si se actualizó, False si no se encontró.
        """
        nodo_actual = self.raiz
        while nodo_actual:
            if nodo_actual.transaccion.id_transaccion == id_transaccion:
                for clave, valor in nuevos_datos.items():
                    setattr(nodo_actual.transaccion, clave, valor)
                return True
            nodo_actual = nodo_actual.siguiente
        return False

    def eliminar_transaccion(self, id_transaccion):
        """
        Elimina una transacción de la lista por su ID.

        Parámetros:
        id_transaccion: ID de la transacción a eliminar.

        Retorna:
        True si se eliminó, False si no se encontró.
        """
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
        """
        Consulta las transacciones por cliente o fecha.

        Parámetros:
        id_cliente: (opcional) ID del cliente a consultar.
        fecha: (opcional) Fecha de la transacción a consultar.

        Retorna:
        Lista de transacciones que cumplen los criterios.
        """
        nodo_actual = self.raiz
        resultados = []
        while nodo_actual:
            t = nodo_actual.transaccion
            if (id_cliente is None or t.id_cliente == id_cliente) and (fecha is None or t.fecha == fecha):
                resultados.append(t)
            nodo_actual = nodo_actual.siguiente
        return resultados