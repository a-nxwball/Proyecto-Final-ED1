from datetime import date, timedelta

try:
    from .ModuloProductos import ListaProductos, Producto
except ImportError:
    from ModuloProductos import ListaProductos, Producto

class ModuloRotaciones:
    # Lógica de rotación, temporada y rebajas
    def __init__(self, lista_productos: ListaProductos):
        if not isinstance(lista_productos, ListaProductos):
            raise TypeError("Se requiere una instancia de ListaProductos.")
        self.lista_productos = lista_productos

    def verificar_temporada(self, producto_id: int) -> bool | None:
        # Verifica si un producto es de temporada
        productos_encontrados = self.lista_productos.consultar_producto(id_producto=producto_id)
        if productos_encontrados:
            return productos_encontrados[0].temporalidad
        return None

    def verificar_rebaja(self, producto_id: int) -> float | None:
        # Verifica si un producto tiene rebaja
        productos_encontrados = self.lista_productos.consultar_producto(id_producto=producto_id)
        if productos_encontrados:
            return productos_encontrados[0].rebaja
        return None

    def obtener_productos_temporada(self) -> list[Producto]:
        # Devuelve productos de temporada
        productos_temporada = []
        nodo_actual = self.lista_productos.raiz
        while nodo_actual:
            if nodo_actual.producto.temporalidad:
                productos_temporada.append(nodo_actual.producto)
            nodo_actual = nodo_actual.siguiente
        return productos_temporada

    def obtener_productos_rebajados(self) -> list[Producto]:
        # Devuelve productos con rebaja
        productos_rebajados = []
        nodo_actual = self.lista_productos.raiz
        while nodo_actual:
            if nodo_actual.producto.rebaja > 0:
                productos_rebajados.append(nodo_actual.producto)
            nodo_actual = nodo_actual.siguiente
        return productos_rebajados

    def aplicar_rebajas_expiracion(self, dias_antes: int = 5, porcentaje_rebaja: float = 0.2) -> int:
        # Aplica rebaja a productos cercanos a expirar
        hoy = date.today()  # Fecha actual del sistema
        fecha_limite = hoy + timedelta(days=dias_antes)  # Fecha límite para considerar productos próximos a expirar
        nodo_actual = self.lista_productos.raiz  # Nodo actual de la lista doblemente enlazada de productos
        productos_actualizados = 0  # Contador de productos a los que se les aplicó rebaja
        while nodo_actual:
            p = nodo_actual.producto  # Instancia de Producto en el nodo actual
            if p.fecha_expiracion:
                try:
                    fecha_exp_str = p.fecha_expiracion  # Fecha de expiración en formato string o date
                    if isinstance(fecha_exp_str, date):
                        fecha_exp = fecha_exp_str  # Ya es un objeto date
                    elif isinstance(fecha_exp_str, str):
                        fecha_exp = date.fromisoformat(fecha_exp_str)  # Convertir string ISO a date
                    else:
                        raise TypeError("Formato de fecha de expiración no válido.")
                    # Rebaja por expiración: si el producto expira entre hoy y la fecha límite y no tiene rebaja activa
                    if hoy <= fecha_exp <= fecha_limite and p.rebaja == 0.0:
                        actualizado = self.lista_productos.actualizar_producto(
                            p.id_producto,
                            {'rebaja': porcentaje_rebaja}
                        )
                        if actualizado:
                            print(f"💸 Rebaja ({porcentaje_rebaja*100}%) aplicada al producto ID {p.id_producto} ({p.nombre}) por proximidad de expiración.")
                            productos_actualizados += 1
                        else:
                            print(f"Error al intentar actualizar la rebaja para el producto ID {p.id_producto}.")
                    # Rebaja por temporada lluviosa/seca (ejemplo: meses 5-11 lluviosa, 12-4 seca)
                    mes = hoy.month  # Mes actual (1-12)
                    if p.temporalidad:
                        # Si es temporada lluviosa y no tiene rebaja activa
                        if 5 <= mes <= 11 and p.rebaja == 0.0:
                            actualizado = self.lista_productos.actualizar_producto(
                                p.id_producto,
                                {'rebaja': 0.15}
                            )
                            if actualizado:
                                print(f"🌧️ Rebaja de temporada lluviosa aplicada a {p.nombre}.")
                                productos_actualizados += 1
                        # Si es temporada seca y no tiene rebaja activa
                        elif (mes < 5 or mes > 11) and p.rebaja == 0.0:
                            actualizado = self.lista_productos.actualizar_producto(
                                p.id_producto,
                                {'rebaja': 0.10}
                            )
                            if actualizado:
                                print(f"☀️ Rebaja de temporada seca aplicada a {p.nombre}.")
                                productos_actualizados += 1
                except (ValueError, TypeError) as e:
                    print(f"Advertencia: No se pudo procesar fecha de expiración para producto ID {p.id_producto}. Razón: {e}")
            nodo_actual = nodo_actual.siguiente
        if productos_actualizados == 0:
            print("No se aplicaron nuevas rebajas por expiración o temporada en esta ejecución.")
        return productos_actualizados
