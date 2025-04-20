from datetime import date, timedelta

try:
    from .ModuloProductos import ListaProductos, Producto 
except ImportError:
    # Fallback por si se ejecuta como script individual o desde una estructura diferente
    from ModuloProductos import ListaProductos, Producto

class ModuloRotaciones:
    """Gestiona la lógica de rotación, temporada y rebajas de productos."""

    def __init__(self, lista_productos: ListaProductos):
        """Inicializa el módulo con una instancia de ListaProductos."""
        if not isinstance(lista_productos, ListaProductos):
            raise TypeError("Se requiere una instancia de ListaProductos.")
        self.lista_productos = lista_productos

    def verificar_temporada(self, producto_id: int) -> bool | None:
        """
        Verifica si un producto específico está marcado como de temporada.
        Devuelve True si es de temporada, False si no lo es, None si el producto no se encuentra.
        """
        productos_encontrados = self.lista_productos.consultar_producto(id_producto=producto_id)
        if productos_encontrados:
            # Asumiendo que consultar_producto devuelve una lista y el ID es único
            return productos_encontrados[0].temporalidad 
        return None # Producto no encontrado

    def verificar_rebaja(self, producto_id: int) -> float | None:
        """
        Verifica si un producto específico tiene una rebaja aplicada (rebaja > 0).
        Devuelve el valor de la rebaja (ej. 0.2 para 20%) o 0 si no tiene.
        Devuelve None si el producto no se encuentra.
        """
        productos_encontrados = self.lista_productos.consultar_producto(id_producto=producto_id)
        if productos_encontrados:
            return productos_encontrados[0].rebaja
        return None # Producto no encontrado

    def obtener_productos_temporada(self) -> list[Producto]:
        """Devuelve una lista de todos los productos marcados como de temporada."""
        productos_temporada = []
        nodo_actual = self.lista_productos.raiz
        while nodo_actual:
            if nodo_actual.producto.temporalidad:
                productos_temporada.append(nodo_actual.producto)
            nodo_actual = nodo_actual.siguiente
        return productos_temporada

    def obtener_productos_rebajados(self) -> list[Producto]:
        """Devuelve una lista de todos los productos que tienen una rebaja aplicada (rebaja > 0)."""
        productos_rebajados = []
        nodo_actual = self.lista_productos.raiz
        while nodo_actual:
            if nodo_actual.producto.rebaja > 0:
                productos_rebajados.append(nodo_actual.producto)
            nodo_actual = nodo_actual.siguiente
        return productos_rebajados

    def aplicar_rebajas_expiracion(self, dias_antes: int = 5, porcentaje_rebaja: float = 0.2) -> int:
        """
        Aplica una rebaja a productos cercanos a su fecha de expiración.
        Utiliza el método actualizar_producto de ListaProductos.
        Devuelve la cantidad de productos actualizados.
        """
        hoy = date.today()
        fecha_limite = hoy + timedelta(days=dias_antes)
        nodo_actual = self.lista_productos.raiz
        productos_actualizados = 0

        while nodo_actual:
            p = nodo_actual.producto
            if p.fecha_expiracion:
                try:
                    # Asegurarse que fecha_expiracion es un objeto date o string ISO
                    fecha_exp_str = p.fecha_expiracion
                    if isinstance(fecha_exp_str, date):
                         fecha_exp = fecha_exp_str # Ya es objeto date
                    elif isinstance(fecha_exp_str, str):
                         fecha_exp = date.fromisoformat(fecha_exp_str)
                    else:
                         # Si no es ni date ni string, no podemos procesar
                         raise TypeError("Formato de fecha de expiración no válido.")

                    # Comprobar si está en el rango de expiración y no tiene rebaja ya
                    if hoy <= fecha_exp <= fecha_limite and p.rebaja == 0.0:
                        # Actualizar usando el método de ListaProductos
                        actualizado = self.lista_productos.actualizar_producto(
                            p.id_producto, 
                            {'rebaja': porcentaje_rebaja}
                        )
                        if actualizado:
                            print(f"Rebaja ({porcentaje_rebaja*100}%) aplicada al producto ID {p.id_producto} ({p.nombre}) por proximidad de expiración.")
                            productos_actualizados += 1
                        else:
                             print(f"Error al intentar actualizar la rebaja para el producto ID {p.id_producto}.")
                            
                except (ValueError, TypeError) as e:
                    print(f"Advertencia: No se pudo procesar fecha de expiración para producto ID {p.id_producto}. Razón: {e}")
            
            nodo_actual = nodo_actual.siguiente
        
        if productos_actualizados == 0:
            print("No se aplicaron nuevas rebajas por expiración en esta ejecución.")
        
        return productos_actualizados
