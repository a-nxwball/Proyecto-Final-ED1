from datetime import datetime, timedelta

# Lista para guardar los productos
inventario = []

# Clase Producto
class Producto:
    def __init__(self, id_producto, nombre, descripcion, categoria, precio, stock, fecha_expiracion, temporalidad, rebaja=0):
        self.id_producto = id_producto
        self.nombre = nombre
        self.descripcion = descripcion
        self.categoria = categoria
        self.precio = precio
        self.stock = stock
        self.fecha_expiracion = datetime.strptime(fecha_expiracion, "%Y-%m-%d") if fecha_expiracion else None
        self.temporalidad = temporalidad
        self.rebaja = rebaja

    def aplicar_rebaja(self):
        if self.fecha_expiracion:
            dias_restantes = (self.fecha_expiracion - datetime.now()).days
            if dias_restantes <= 5:  # Si le quedan 5 días o menos para expirar
                self.rebaja = 0.20  # 20% de rebaja
                self.precio *= (1 - self.rebaja)

# Funciones

def registrar_producto():
    id_producto = input("ID del producto: ")
    nombre = input("Nombre: ")
    descripcion = input("Descripción: ")
    categoria = input("Categoría: ")
    precio = float(input("Precio: "))
    stock = int(input("Stock: "))
    fecha_expiracion = input("Fecha de expiración (YYYY-MM-DD, dejar vacío si no aplica): ")
    temporalidad = input("¿Es de temporada? (sí/no): ").lower() == "sí"
    
    producto = Producto(id_producto, nombre, descripcion, categoria, precio, stock, fecha_expiracion, temporalidad)
    inventario.append(producto)
    print(f"Producto '{nombre}' registrado con éxito.")

def actualizar_producto():
    id_buscar = input("Ingrese el ID del producto a actualizar: ")
    for producto in inventario:
        if producto.id_producto == id_buscar:
            producto.nombre = input(f"Nuevo nombre ({producto.nombre}): ") or producto.nombre
            producto.descripcion = input(f"Nueva descripción ({producto.descripcion}): ") or producto.descripcion
            producto.categoria = input(f"Nueva categoría ({producto.categoria}): ") or producto.categoria
            producto.precio = float(input(f"Nuevo precio ({producto.precio}): ") or producto.precio)
            producto.stock = int(input(f"Nuevo stock ({producto.stock}): ") or producto.stock)
            fecha_exp = input(f"Nueva fecha de expiración ({producto.fecha_expiracion.date()}): ")
            if fecha_exp:
                producto.fecha_expiracion = datetime.strptime(fecha_exp, "%Y-%m-%d")
            producto.temporalidad = input(f"¿Es de temporada? ({'sí' if producto.temporalidad else 'no'}): ").lower() == "sí"
            print("Producto actualizado.")
            return
    print("Producto no encontrado.")

def eliminar_producto():
    id_eliminar = input("Ingrese el ID del producto a eliminar: ")
    global inventario
    inventario = [p for p in inventario if p.id_producto != id_eliminar]
    print("Producto eliminado, si existía.")

def consultar_producto():
    criterio = input("Buscar por ID o nombre: ").lower()
    for p in inventario:
        if p.id_producto == criterio or p.nombre.lower() == criterio:
            print(vars(p))
            return
    print("Producto no encontrado.")

def aplicar_rebaja():
    for p in inventario:
        p.aplicar_rebaja()
    print("Rebajas aplicadas a productos próximos a expirar.")

# Ejemplo de menú
def menu():
    while True:
        print("\n1. Registrar producto\n2. Actualizar producto\n3. Eliminar producto\n4. Consultar producto\n5. Aplicar rebajas\n6. Salir")
        opcion = input("Seleccione una opción: ")
        if opcion == "1":
            registrar_producto()
        elif opcion == "2":
            actualizar_producto()
        elif opcion == "3":
            eliminar_producto()
        elif opcion == "4":
            consultar_producto()
        elif opcion == "5":
            aplicar_rebaja()
        elif opcion == "6":
            break
        else:
            print("Opción no válida.")

# Ejecutar menú si se desea
menu()