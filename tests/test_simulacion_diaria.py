import sys
import os
import random
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import simpy
from datetime import date, timedelta
from app.ModuloProductos import ListaProductos
from app.ModuloClientes import ListaClientes
from app.ModuloTransacciones import ListaTransacciones
from app.ModuloMovimientos import ListaMovimientos
from app.ModuloRotaciones import ModuloRotaciones
from app.ModuloProveedores import ListaProveedores

class TestSimulacionDiaria(unittest.TestCase):
    def setUp(self):
        self.hoy = date.today()
        self.productos = ListaProductos()
        self.clientes = ListaClientes()
        self.transacciones = ListaTransacciones()
        self.movimientos = ListaMovimientos()
        self.rotaciones = ModuloRotaciones(self.productos)
        self.proveedores = ListaProveedores()
        self.env = simpy.Environment()
        self.env.products = []
        self.env.clientes = []
        self.env.proveedores = []

    # --- Simulación con simpy ---
    def llegada_productos(self, env):
        yield env.timeout(0)
        # Lista de productos y proveedores de ejemplo
        nombres = ["Manzana", "Pera", "Sandía", "Banano", "Fresa", "Melón"]
        descripciones = ["Roja", "Verde", "Grande", "Amarillo", "Temporada", "Expira"]
        categorias = ["Fruta", "Fruta", "Fruta", "Fruta", "Fruta", "Fruta"]
        precios = [1.5, 2.0, 3.0, 1.0, 2.0, 3.0]
        stocks = [50, 30, 20, 40, 10, 5]
        temporalidades = [True, False, True, False, True, False]
        # Proveedores
        proveedores = [
            self.proveedores.registrar_proveedor(f"Proveedor{i}", f"Contacto{i}", f"Dirección{i}")
            for i in range(1, 4)
        ]
        env.proveedores = [p for p in proveedores if p is not None]
        productos_creados = []
        for i in range(len(nombres)):
            producto = self.productos.registrar_producto(
                nombre=nombres[i],
                descripcion=descripciones[i],
                categoria=categorias[i],
                precio=precios[i],
                stock=stocks[i],
                fecha_expiracion=(self.hoy + timedelta(days=random.randint(1, 15))).isoformat(),
                temporalidad=temporalidades[i],
                rebaja=0.0
            )
            productos_creados.append(producto)
        env.products = productos_creados

    def llegada_clientes(self, env):
        yield env.timeout(0)
        nombres = ["Juan Pérez", "Ana Gómez", "Carlos Ruiz", "Lucía Torres"]
        tipos = ["minorista", "mayorista"]
        clientes_creados = []
        for i, nombre in enumerate(nombres):
            cliente = self.clientes.registrar_cliente(
                nombre=nombre,
                contacto=f"Contacto{i}",
                direccion=f"Dirección{i}",
                tipo_cliente=random.choice(tipos),
                credito=random.randint(0, 200)
            )
            clientes_creados.append(cliente)
        env.clientes = clientes_creados

    def actualizar_stock(self, env):
        yield env.timeout(1)
        # Selecciona aleatoriamente productos para actualizar stock
        productos = [p for p in env.products if p is not None]
        if productos:
            seleccionados = random.sample(productos, min(2, len(productos)))
            for p in seleccionados:
                self.productos.actualizar_producto(p.id_producto, {"stock": p.stock + random.randint(1, 20)})

    def aplicar_rebajas(self, env):
        yield env.timeout(2)
        n_rebajas = self.rotaciones.aplicar_rebajas_expiracion(dias_antes=2, porcentaje_rebaja=0.5)
        self.env.n_rebajas = n_rebajas

    def registrar_venta(self, env):
        yield env.timeout(3)
        productos = [p for p in env.products if p is not None]
        clientes = [c for c in env.clientes if c is not None]
        if not productos or not clientes:
            return
        # Selecciona aleatoriamente cliente y productos para la venta
        cliente = random.choice(clientes)
        productos_venta = random.sample(productos, min(2, len(productos)))
        total = sum(p.precio for p in productos_venta)
        venta = self.transacciones.registrar_transaccion(
            id_cliente=cliente.id_cliente,
            productos=[p.id_producto for p in productos_venta],
            total=total,
            fecha=self.hoy.isoformat(),
            tipo_pago=random.choice(["efectivo", "tarjeta", "crédito"]),
            estado=random.choice(["completada", "pendiente"])
        )
        if venta:
            self.movimientos.registrar_movimiento(
                id_transaccion=venta.id_transaccion,
                fecha=self.hoy.isoformat(),
                tipo="venta"
            )

    def consultar_movimientos(self, env):
        yield env.timeout(4)
        movs = self.movimientos.consultar_movimientos(fecha_consulta=self.hoy.isoformat())
        self.env.movs = movs

    def consultar_temporada_rebajas(self, env):
        yield env.timeout(5)
        self.env.temporada = self.rotaciones.obtener_productos_temporada()
        self.env.rebajados = self.rotaciones.obtener_productos_rebajados()

    def test_flujo_diario_simpy(self):
        self.env.process(self.llegada_productos(self.env))
        self.env.process(self.llegada_clientes(self.env))
        self.env.process(self.actualizar_stock(self.env))
        self.env.process(self.aplicar_rebajas(self.env))
        self.env.process(self.registrar_venta(self.env))
        self.env.process(self.consultar_movimientos(self.env))
        self.env.process(self.consultar_temporada_rebajas(self.env))
        self.env.run(until=6)

        # Verifica que hay productos de temporada
        self.assertTrue(any(p.temporalidad for p in self.env.temporada))
        # Verifica que hay productos rebajados por expiración
        self.assertTrue(any(p.rebaja > 0 for p in self.env.rebajados))
        # Verifica que hay movimientos registrados hoy
        self.assertTrue(any(m.fecha == self.hoy.isoformat() for m in self.env.movs))
        # Verifica que se aplicó al menos una rebaja
        self.assertGreaterEqual(self.env.n_rebajas, 1)

    # --- Tests unitarios de Productos ---
    def test_registrar_y_consultar_producto(self):
        p = self.productos.registrar_producto(
            nombre="Manzana", descripcion="Roja", categoria="Fruta",
            precio=1.5, stock=10, fecha_expiracion="2099-12-31", temporalidad=True, rebaja=0.0
        )
        self.assertIsNotNone(p)
        res = self.productos.consultar_producto(id_producto=p.id_producto)
        self.assertTrue(len(res) == 1)
        self.assertEqual(res[0].nombre, "Manzana")

    def test_actualizar_producto(self):
        p = self.productos.registrar_producto(
            nombre="Pera", descripcion="Verde", categoria="Fruta",
            precio=2.0, stock=5
        )
        actualizado = self.productos.actualizar_producto(p.id_producto, {"precio": 2.5})
        self.assertTrue(actualizado)
        res = self.productos.consultar_producto(id_producto=p.id_producto)
        self.assertEqual(res[0].precio, 2.5)

    def test_eliminar_producto(self):
        p = self.productos.registrar_producto(
            nombre="Banano", descripcion="Amarillo", categoria="Fruta",
            precio=1.0, stock=20
        )
        eliminado = self.productos.eliminar_producto(p.id_producto)
        self.assertTrue(eliminado)
        res = self.productos.consultar_producto(id_producto=p.id_producto)
        self.assertEqual(len(res), 0)

    # --- Tests unitarios de Proveedores ---
    def test_registrar_y_consultar_proveedor(self):
        p = self.proveedores.registrar_proveedor("ProveedorTest", "123456", "Calle Falsa 123")
        self.assertIsNotNone(p)
        res = self.proveedores.consultar_proveedor(p.id_proveedor)
        self.assertIsNotNone(res)
        self.assertEqual(res.nombre, "ProveedorTest")

    def test_actualizar_proveedor(self):
        p = self.proveedores.registrar_proveedor("Proveedor2", "654321", "Otra Calle")
        actualizado = self.proveedores.actualizar_proveedor(p.id_proveedor, {"nombre": "ProveedorMod"})
        self.assertTrue(actualizado)
        res = self.proveedores.consultar_proveedor(p.id_proveedor)
        self.assertEqual(res.nombre, "ProveedorMod")

    def test_eliminar_proveedor(self):
        p = self.proveedores.registrar_proveedor("Proveedor3", "000000", "Calle 3")
        eliminado = self.proveedores.eliminar_proveedor(p.id_proveedor)
        self.assertTrue(eliminado)
        res = self.proveedores.consultar_proveedor(p.id_proveedor)
        self.assertIsNone(res)

    # --- Tests unitarios de Clientes ---
    def test_registrar_y_consultar_cliente(self):
        c = self.clientes.registrar_cliente("ClienteTest", "999999", "Calle Cliente", "minorista", 100)
        self.assertIsNotNone(c)
        res = self.clientes.consultar_cliente(id_cliente=c.id_cliente)
        self.assertTrue(len(res) == 1)
        self.assertEqual(res[0].nombre, "ClienteTest")

    def test_actualizar_cliente(self):
        c = self.clientes.registrar_cliente("Cliente2", "888888", "Otra Calle", "mayorista", 50)
        actualizado = self.clientes.actualizar_cliente(c.id_cliente, {"credito": 200})
        self.assertTrue(actualizado)
        res = self.clientes.consultar_cliente(id_cliente=c.id_cliente)
        self.assertEqual(res[0].credito, 200)

    def test_eliminar_cliente(self):
        c = self.clientes.registrar_cliente("Cliente3", "777777", "Calle 3", "minorista", 0)
        eliminado = self.clientes.eliminar_cliente(c.id_cliente)
        self.assertTrue(eliminado)
        res = self.clientes.consultar_cliente(id_cliente=c.id_cliente)
        self.assertEqual(len(res), 0)

    # --- Tests unitarios de Transacciones ---
    def test_registrar_y_consultar_transaccion(self):
        t = self.transacciones.registrar_transaccion(
            id_cliente=1, productos=["Manzana", "Pera"], total=10.0,
            fecha="2099-01-01", tipo_pago="efectivo", estado="completada"
        )
        self.assertIsNotNone(t)
        res = self.transacciones.consultar_transacciones(id_cliente=1)
        self.assertTrue(any(tr.id_transaccion == t.id_transaccion for tr in res))

    def test_actualizar_transaccion(self):
        t = self.transacciones.registrar_transaccion(
            id_cliente=1, productos=["Banano"], total=5.0,
            fecha="2099-01-02", tipo_pago="tarjeta", estado="pendiente"
        )
        actualizado = self.transacciones.actualizar_transaccion(t.id_transaccion, {"estado": "completada"})
        self.assertTrue(actualizado)
        res = self.transacciones.consultar_transacciones(id_cliente=1)
        self.assertTrue(any(tr.estado == "completada" for tr in res if tr.id_transaccion == t.id_transaccion))

    def test_eliminar_transaccion(self):
        t = self.transacciones.registrar_transaccion(
            id_cliente=1, productos=["Uva"], total=3.0,
            fecha="2099-01-03", tipo_pago="efectivo", estado="pendiente"
        )
        eliminado = self.transacciones.eliminar_transaccion(t.id_transaccion)
        self.assertTrue(eliminado)
        res = self.transacciones.consultar_transacciones(id_cliente=1)
        self.assertFalse(any(tr.id_transaccion == t.id_transaccion for tr in res))

    # --- Tests unitarios de Movimientos ---
    def test_registrar_y_consultar_movimiento(self):
        m = self.movimientos.registrar_movimiento(
            id_transaccion=1, fecha="2099-01-01", tipo="venta"
        )
        self.assertIsNotNone(m)
        res = self.movimientos.consultar_movimientos(fecha_consulta="2099-01-01")
        self.assertTrue(any(mv.id_estado == m.id_estado for mv in res))

    def test_eliminar_movimiento_por_id_transaccion(self):
        m = self.movimientos.registrar_movimiento(
            id_transaccion=2, fecha="2099-01-02", tipo="compra"
        )
        eliminado = self.movimientos.eliminar_movimiento_por_id_transaccion(m.id_transaccion)
        self.assertTrue(eliminado)
        res = self.movimientos.consultar_movimientos()
        self.assertFalse(any(mv.id_transaccion == m.id_transaccion for mv in res))

    # --- Tests unitarios de Rotaciones ---
    def test_verificar_temporada(self):
        p = self.productos.registrar_producto(
            nombre="Fresa", descripcion="Temporada", categoria="Fruta",
            precio=2.0, stock=10, fecha_expiracion="2099-12-31", temporalidad=True, rebaja=0.0
        )
        es_temporada = self.rotaciones.verificar_temporada(p.id_producto)
        self.assertTrue(es_temporada)

    def test_verificar_rebaja(self):
        p = self.productos.registrar_producto(
            nombre="Fresa", descripcion="Temporada", categoria="Fruta",
            precio=2.0, stock=10, fecha_expiracion="2099-12-31", temporalidad=True, rebaja=0.0
        )
        rebaja = self.rotaciones.verificar_rebaja(p.id_producto)
        self.assertEqual(rebaja, 0.0)

    def test_obtener_productos_temporada(self):
        p = self.productos.registrar_producto(
            nombre="Fresa", descripcion="Temporada", categoria="Fruta",
            precio=2.0, stock=10, fecha_expiracion="2099-12-31", temporalidad=True, rebaja=0.0
        )
        lista = self.rotaciones.obtener_productos_temporada()
        self.assertTrue(any(prod.id_producto == p.id_producto for prod in lista))

    def test_aplicar_rebajas_expiracion(self):
        p = self.productos.registrar_producto(
            nombre="Melón", descripcion="Expira", categoria="Fruta",
            precio=3.0, stock=5, fecha_expiracion="2099-01-01", temporalidad=False, rebaja=0.0
        )
        self.productos.actualizar_producto(p.id_producto, {"fecha_expiracion": "2099-01-01"})
        n = self.rotaciones.aplicar_rebajas_expiracion(dias_antes=36500, porcentaje_rebaja=0.5)
        self.assertGreaterEqual(n, 1)
        p_actualizado = self.productos.consultar_producto(id_producto=p.id_producto)[0]
        self.assertEqual(p_actualizado.rebaja, 0.5)

if __name__ == "__main__":
    unittest.main()
