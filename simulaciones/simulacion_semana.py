import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import simpy
import random
from datetime import date, timedelta
import sqlite3

from app.ModuloProductos import ListaProductos
from app.ModuloClientes import ListaClientes
from app.ModuloTransacciones import ListaTransacciones
from app.ModuloMovimientos import ListaMovimientos
from app.ModuloRotaciones import ModuloRotaciones
from app.ModuloProveedores import ListaProveedores

UMBRAL_STOCK = 40  # Stock mínimo antes de activar reabastecimiento automático
STOCK_OBJETIVO = 30  # Nivel de stock deseado tras reabastecimiento
MARGEN_OBJETIVO = 0.25  # Margen de ganancia objetivo para ajustar precios
ROTACION_MINIMA = 3  # Número mínimo de ventas por semana para considerar buena rotación

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # Ruta base del proyecto (directorio raíz)
DB_PATH = os.path.join(BASE_DIR, "bd", "Abarrotería.db")  # Ruta absoluta al archivo de la base de datos SQLite
TABLAS = [
    "Rotaciones",      # Tabla para registrar rotaciones de productos
    "Movimientos",     # Tabla para registrar movimientos de inventario
    "Transacciones",   # Tabla para registrar ventas y compras
    "Clientes",        # Tabla de clientes
    "Proveedores",     # Tabla de proveedores
    "Productos"        # Tabla de productos
]

def limpiar_cache_pycache(root_dir):
    # Elimina carpetas __pycache__ y archivos .pyc en el directorio dado.
    # root_dir: ruta base donde buscar y limpiar cachés de Python
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if "__pycache__" in dirnames:
            pycache_path = os.path.join(dirpath, "__pycache__")
            try:
                import shutil
                shutil.rmtree(pycache_path)
                print(f"Eliminado: {pycache_path}")
            except Exception as e:
                print(f"Error al eliminar {pycache_path}: {e}")
        for filename in filenames:
            if filename.endswith(".pyc"):
                pyc_path = os.path.join(dirpath, filename)
                try:
                    os.remove(pyc_path)
                    print(f"Eliminado: {pyc_path}")
                except Exception as e:
                    print(f"Error al eliminar {pyc_path}: {e}")

def resetear_bd(db_path=DB_PATH, tablas=TABLAS):
    # Limpia todas las tablas de la base de datos y reinicia los autoincrementos.
    if not os.path.exists(db_path):
        print("No existe la base de datos:", db_path)
        return
    conexion = sqlite3.connect(db_path)
    try:
        cursor = conexion.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF")
        for tabla in tablas:
            cursor.execute(f"DELETE FROM {tabla}")
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{tabla}'")
        conexion.commit()
        print("Base de datos limpiada y autoincrementos reiniciados.")
    except Exception as e:
        print("Error al limpiar la base de datos:", e)
        conexion.rollback()
    finally:
        conexion.close()
    print("Eliminando cachés (__pycache__ y .pyc)...")
    limpiar_cache_pycache(BASE_DIR)
    print("Limpieza de caché completada.")

def llegada_productos(env, productos, proveedores):
    # Registra productos iniciales en el sistema, asignando proveedores según la categoría.
    nombres = [
        "Mango", "Piña", "Guayaba", "Maracuyá", "Naranja", "Plátano", "Sandía", "Fresa", "Manzana", "Pera", "Melón", "Banano", "Uva", "Durazno",
        "Lechuga", "Tomate", "Zanahoria", "Cebolla", "Papa", "Brócoli",
        "Lenteja", "Frijol", "Garbanzo",
        "Arroz", "Maíz", "Avena",
        "Pollo", "Res", "Cerdo",
        "Leche", "Queso", "Yogur"
    ]
    descripciones = [
        "Dulce", "Tropical", "Aromática", "Ácida", "Jugosa", "Verde", "Grande", "Roja", "Roja", "Verde", "Grande", "Amarillo", "Pequeña", "Suave",
        "Fresca", "Maduro", "Orgánica", "Blanca", "Andina", "Verde",
        "Seca", "Negro", "Chico",
        "Integral", "Dulce", "Fibra",
        "Pechuga", "Lomo", "Costilla",
        "Entera", "Mozzarella", "Natural"
    ]
    categorias = (
        ["Fruta"] * 14 +
        ["Verdura"] * 6 +
        ["Menestra"] * 3 +
        ["Cereal"] * 3 +
        ["Carne"] * 3 +
        ["Lacteo"] * 3
    )
    precios = [1.2, 1.5, 1.3, 1.4, 1.1, 1.0, 2.0, 2.2, 1.5, 2.0, 3.0, 1.0, 2.5, 2.8,
               0.8, 0.9, 1.1, 0.7, 0.6, 1.3,
               1.0, 1.1, 1.2,
               0.7, 0.8, 1.0,
               4.0, 5.0, 4.5,
               1.2, 2.0, 1.8]
    stocks = [30, 25, 20, 15, 40, 35, 10, 12, 50, 30, 20, 40, 18, 22,
              25, 30, 20, 18, 35, 15,
              20, 22, 18,
              40, 35, 30,
              15, 12, 10,
              25, 20, 18]
    temporalidades = [False] * len(nombres)
    proveedores_por_categoria = {}
    nodo = proveedores.raiz
    while nodo:
        for cat in ["Fruta", "Verdura", "Menestra", "Cereal", "Carne", "Lacteo"]:
            if cat.lower() in nodo.proveedor.nombre.lower():
                proveedores_por_categoria[cat] = nodo.proveedor
        nodo = nodo.siguiente
    for i in range(len(nombres)):
        categoria = categorias[i]
        proveedor = proveedores_por_categoria.get(categoria)
        productos.registrar_producto(
            nombre=nombres[i],
            descripcion=descripciones[i],
            categoria=categoria,
            precio=precios[i],
            stock=stocks[i],
            fecha_expiracion=(date.today() + timedelta(days=random.randint(10, 14))).isoformat(),
            temporalidad=temporalidades[i],
            rebaja=0.0,
            id_proveedor=proveedor.id_proveedor if proveedor else None
        )
    yield env.timeout(0)

def llegada_clientes(env, clientes):
    # Registra clientes iniciales en el sistema.
    nombres = ["Juan Pérez", "Ana Gómez", "Carlos Ruiz", "Lucía Torres"]
    tipos = ["minorista", "mayorista"]
    for i, nombre in enumerate(nombres):
        clientes.registrar_cliente(
            nombre=nombre,
            contacto=f"Contacto{i}",
            direccion=f"Dirección{i}",
            tipo_cliente=random.choice(tipos),
            credito=random.randint(0, 200)
        )
    yield env.timeout(0)

def llegada_proveedores(env, proveedores):
    # Registra proveedores iniciales en el sistema.
    proveedores_info = [
        {"nombre": "Frutas Panamá", "categoria": "Fruta"},
        {"nombre": "Verduras Selectas", "categoria": "Verdura"},
        {"nombre": "Menestras del Valle", "categoria": "Menestra"},
        {"nombre": "Cerealistas S.A.", "categoria": "Cereal"},
        {"nombre": "Carnes Premium", "categoria": "Carne"},
        {"nombre": "Lácteos Panamá", "categoria": "Lacteo"},
    ]
    for i, info in enumerate(proveedores_info):
        proveedores.registrar_proveedor(
            nombre=info["nombre"],
            contacto=f"ContactoProv{i}",
            direccion=f"DirecciónProv{i}"
        )
    yield env.timeout(0)

def aviso_venta(cliente, productos_venta, total):
    # Imprime un aviso de venta realizada.
    print("\n" + "="*50)
    print("VENTA REALIZADA")
    print("="*50)
    print(f"🛒 Cliente: '{cliente.nombre}' (ID: {cliente.id_cliente})")
    print("Productos vendidos:")
    for p in productos_venta:
        print(f"  - {p.nombre} (ID: {p.id_producto})")
    print(f"Total venta: ${total:.2f}")
    print("="*50 + "\n")

def aviso_compra(proveedor, producto, cantidad, total):
    # Imprime un aviso de compra o reabastecimiento realizado.
    print("\n" + "="*50)
    print("COMPRA/REABASTECIMIENTO")
    print("="*50)
    print(f"🚚 Se compraron {cantidad} unidades de '{producto.nombre}' (ID: {producto.id_producto})")
    print(f"Proveedor: '{proveedor.nombre}' (ID: {proveedor.id_proveedor})")
    print(f"Total gastado: ${total:.2f}")
    print("="*50 + "\n")

def caso_temporada(env, productos):
    # Marca productos como de temporada si corresponde.
    yield env.timeout(1)
    productos_panamenos_temporada = [
        "mango", "piña", "guayaba", "maracuyá", "naranja", "plátano", "sandía", "fresa"
    ]
    for p in productos.consultar_producto():
        if any(nombre in p.nombre.lower() for nombre in productos_panamenos_temporada):
            productos.actualizar_producto(p.id_producto, {"temporalidad": True})

def caso_rebajas(env, rotaciones):
    # Aplica rebajas a productos próximos a expirar durante la semana.
    for dia in range(7):
        yield env.timeout(1)
        n_rebajas = rotaciones.aplicar_rebajas_expiracion(dias_antes=2, porcentaje_rebaja=0.5)
        if n_rebajas > 0:
            print(f"💸 Día {dia+1}: Se aplicaron {n_rebajas} rebaja(s) a productos próximos a expirar.")
        else:
            print(f"💸 Día {dia+1}: No se aplicaron rebajas por expiración.")

def ajuste_inteligente_precios_stock(productos, transacciones, movimientos, semana_inicio, semana_fin, margen_objetivo=MARGEN_OBJETIVO, rotacion_minima=ROTACION_MINIMA):
    # Ajusta precios y stock de productos según margen y rotación semanal.
    ajustes_realizados = []
    for p in productos.consultar_producto():
        ventas = []
        compras = []
        nodo_t = transacciones.raiz
        while nodo_t:
            t = nodo_t.transaccion
            if t.fecha >= semana_inicio and t.fecha <= semana_fin:
                mov = movimientos.consultar_movimiento_por_id_transaccion(t.id_transaccion)
                if mov and mov.tipo == "venta":
                    if isinstance(t.productos, list):
                        if any(
                            (isinstance(x, dict) and x.get("id") == p.id_producto) or
                            (isinstance(x, int) and x == p.id_producto)
                            for x in t.productos
                        ):
                            ventas.append(t)
                    elif str(p.id_producto) in str(t.productos):
                        ventas.append(t)
                if mov and mov.tipo == "compra":
                    if isinstance(t.productos, list):
                        if any(
                            (isinstance(x, dict) and x.get("id") == p.id_producto) or
                            (isinstance(x, int) and x == p.id_producto)
                            for x in t.productos
                        ):
                            compras.append(t)
                    elif str(p.id_producto) in str(t.productos):
                        compras.append(t)
            nodo_t = nodo_t.siguiente

        total_ventas = sum(t.total for t in ventas)
        total_compras = sum(t.total for t in compras)
        num_ventas = len(ventas)

        if total_ventas > 0 and total_compras > 0:
            margen_real = (total_ventas - total_compras) / total_ventas
        else:
            margen_real = 0

        rotacion = num_ventas

        precio_anterior = p.precio
        if margen_real < margen_objetivo:
            nuevo_precio = round(precio_anterior * 1.10, 2)
            productos.actualizar_producto(p.id_producto, {"precio": nuevo_precio})
            ajustes_realizados.append(f"[Ajuste] Producto {p.nombre} (ID {p.id_producto}): Precio subido de {precio_anterior} a {nuevo_precio} por margen bajo ({margen_real:.2f})")
        elif margen_real > margen_objetivo + 0.15:
            nuevo_precio = round(precio_anterior * 0.95, 2)
            productos.actualizar_producto(p.id_producto, {"precio": nuevo_precio})
            ajustes_realizados.append(f"[Ajuste] Producto {p.nombre} (ID {p.id_producto}): Precio bajado de {precio_anterior} a {nuevo_precio} por margen alto ({margen_real:.2f})")

        if p.stock > STOCK_OBJETIVO + 20 and rotacion < rotacion_minima:
            nuevo_stock_obj = max(10, STOCK_OBJETIVO - 10)
            productos.actualizar_producto(p.id_producto, {"stock_objetivo": nuevo_stock_obj})
            ajustes_realizados.append(f"[Ajuste] Producto {p.nombre} (ID {p.id_producto}): Stock objetivo ajustado a {nuevo_stock_obj} por sobrestock y baja rotación")
        elif p.stock < UMBRAL_STOCK and rotacion >= rotacion_minima:
            nuevo_umbral = max(5, UMBRAL_STOCK - 5)
            productos.actualizar_producto(p.id_producto, {"umbral_stock": nuevo_umbral})
            ajustes_realizados.append(f"[Ajuste] Producto {p.nombre} (ID {p.id_producto}): Umbral stock ajustado a {nuevo_umbral} por substock y alta rotación")

        if rotacion < rotacion_minima or (hasattr(p, "fecha_expiracion") and (date.fromisoformat(p.fecha_expiracion) - date.today()).days <= 2):
            precio_rebaja_anterior = p.precio
            nuevo_precio_rebaja = round(precio_rebaja_anterior * 0.8, 2)
            productos.actualizar_producto(p.id_producto, {"precio": nuevo_precio_rebaja, "rebaja": 0.2})
            ajustes_realizados.append(f"[Ajuste] Producto {p.nombre} (ID {p.id_producto}): Rebaja aplicada, nuevo precio {nuevo_precio_rebaja}")
    return ajustes_realizados

def reporte_ajustes(ajustes_realizados):
    # Imprime un reporte de los ajustes realizados en precios y stock.
    print("\n" + "="*60)
    print("REPORTE DE AJUSTES DE PRECIOS Y STOCK".center(60))
    print("="*60 + "\n")
    if not ajustes_realizados:
        print("No se realizaron ajustes de precios ni stock en la semana.\n")
    else:
        for ajuste in ajustes_realizados:
            print(ajuste)
        print()
    print("="*60 + "\n")

def reporte_final(productos, movimientos, rotaciones, transacciones):
    # Imprime el reporte final de la semana con información relevante.
    print("\n" + "="*60)
    print("REPORTE FINAL DE LA SEMANA".center(60))
    print("="*60 + "\n")
    print(">>> [REPORTE TRANSACCIONAL FINAL]:\n")
    fecha_ini = date.today().isoformat()
    fecha_fin = (date.today() + timedelta(days=6)).isoformat()
    transacciones.reporte_transaccional_final(
        movimientos_lista=movimientos,
        fecha_inicio=fecha_ini,
        fecha_fin=fecha_fin
    )
    print("\n" + "-"*60 + "\n")
    print(">>> [REPORTE LOGÍSTICO FINAL]:\n")
    movimientos.reporte_logistico_final(
        lista_productos=productos,
        fecha_inicio=fecha_ini,
        fecha_fin=fecha_fin
    )
    print("\n" + "-"*60 + "\n")
    print(">>> [INFORME] Productos de temporada:\n")
    temporada = rotaciones.obtener_productos_temporada()
    if temporada:
        for p in temporada:
            print(vars(p))
        print()
    else:
        print("No hay productos de temporada.\n")
    print(">>> [INFORME] Productos rebajados:\n")
    rebajados = rotaciones.obtener_productos_rebajados()
    if rebajados:
        for p in rebajados:
            print(vars(p))
        print()
    else:
        print("No hay productos rebajados.\n")
    print("="*60 + "\n")

def main():
    # Función principal que ejecuta la simulación semanal.
    resetear_bd()
    env = simpy.Environment()
    productos = ListaProductos()
    clientes = ListaClientes()
    transacciones = ListaTransacciones()
    movimientos = ListaMovimientos()
    rotaciones = ModuloRotaciones(productos)
    proveedores = ListaProveedores()
    cliente_inventario = clientes.registrar_cliente(
        nombre="Inventario", contacto="N/A", direccion="N/A", tipo_cliente="interno", credito=0
    )
    id_cliente_inventario = cliente_inventario.id_cliente if cliente_inventario else 1

    def caso_movimientos(env, productos, clientes, transacciones, movimientos, proveedores):
        # Simula ventas diarias y reabastecimientos automáticos durante la semana.
        for dia in range(7):
            yield env.timeout(1)
            productos_lista = productos.consultar_producto()
            clientes_lista = clientes.consultar_cliente()
            if not productos_lista or not clientes_lista:
                continue
            clientes_real = [c for c in clientes_lista if c.tipo_cliente not in ("proveedor", "interno")]
            if not clientes_real:
                continue
            cliente = random.choice(clientes_real)
            productos_venta = random.sample(productos_lista, min(2, len(productos_lista)))
            total = sum(p.precio for p in productos_venta)
            aviso_venta(cliente, productos_venta, total)
            for p in productos_venta:
                nuevo_stock = max(0, p.stock - 1)
                productos.actualizar_producto(p.id_producto, {"stock": nuevo_stock})
                if nuevo_stock < UMBRAL_STOCK:
                    proveedores_lista = []
                    nodo = proveedores.raiz
                    while nodo:
                        proveedores_lista.append(nodo.proveedor)
                        nodo = nodo.siguiente
                    if proveedores_lista:
                        proveedor = random.choice(proveedores_lista)
                        cantidad_restock = max(0, STOCK_OBJETIVO - nuevo_stock)
                        if cantidad_restock == 0:
                            continue
                        productos.actualizar_producto(p.id_producto, {"stock": nuevo_stock + cantidad_restock})
                        precio_compra = p.precio
                        total_compra = precio_compra * cantidad_restock
                        aviso_compra(proveedor, p, cantidad_restock, total_compra)
                        compra = transacciones.registrar_transaccion(
                            id_cliente=id_cliente_inventario,
                            id_proveedor=proveedor.id_proveedor,
                            productos=[{"id": p.id_producto, "cantidad": cantidad_restock}],
                            total=total_compra,
                            fecha=(date.today() + timedelta(days=dia)).isoformat(),
                            tipo_pago=f"compra a proveedor {proveedor.nombre}",
                            estado="completada"
                        )
                        if compra:
                            movimientos.registrar_movimiento(
                                id_transaccion=compra.id_transaccion,
                                fecha=(date.today() + timedelta(days=dia)).isoformat(),
                                tipo="compra"
                            )
            venta = transacciones.registrar_transaccion(
                id_cliente=cliente.id_cliente,
                id_proveedor=None,
                productos=[p.id_producto for p in productos_venta],
                total=total,
                fecha=(date.today() + timedelta(days=dia)).isoformat(),
                tipo_pago=random.choice(["efectivo", "tarjeta", "crédito"]),
                estado=random.choice(["completada", "pendiente"])
            )
            if venta:
                movimientos.registrar_movimiento(
                    id_transaccion=venta.id_transaccion,
                    fecha=(date.today() + timedelta(days=dia)).isoformat(),
                    tipo="venta"
                )

    env.process(llegada_proveedores(env, proveedores))
    env.process(llegada_productos(env, productos, proveedores))
    env.process(llegada_clientes(env, clientes))
    env.process(caso_temporada(env, productos))
    env.process(caso_rebajas(env, rotaciones))
    env.process(caso_movimientos(env, productos, clientes, transacciones, movimientos, proveedores))
    env.run(until=8)
    semana_inicio = date.today().isoformat()
    semana_fin = (date.today() + timedelta(days=6)).isoformat()
    ajustes_realizados = ajuste_inteligente_precios_stock(productos, transacciones, movimientos, semana_inicio, semana_fin)
    reporte_ajustes(ajustes_realizados)
    reporte_final(productos, movimientos, rotaciones, transacciones)

if __name__ == "__main__":
    main()
