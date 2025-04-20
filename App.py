import sys
from app.ModuloProductos import ListaProductos
from app.ModuloProveedores import ListaProveedores
from app.ModuloClientes import ListaClientes
from app.ModuloTransacciones import ListaTransacciones
from app.ModuloMovimientos import ListaMovimientos
from app.ModuloRotaciones import ModuloRotaciones

def menu_principal():
    print("\n--- SISTEMA DE GESTIÓN DE INVENTARIO ---")
    print("1. Productos")
    print("2. Proveedores")
    print("3. Clientes")
    print("4. Transacciones")
    print("5. Movimientos")
    print("6. Rotaciones")
    print("0. Salir")

def input_int(prompt, allow_empty=False):
    while True:
        val = input(prompt)
        if allow_empty and val.strip() == "":
            return None
        try:
            return int(val)
        except ValueError:
            print("Por favor, ingrese un número válido.")

def input_float(prompt, allow_empty=False):
    while True:
        val = input(prompt)
        if allow_empty and val.strip() == "":
            return None
        try:
            return float(val)
        except ValueError:
            print("Por favor, ingrese un número válido.")

def menu_productos(lista):
    while True:
        print("\n--- Gestión de Productos ---")
        print("1. Registrar producto")
        print("2. Consultar producto")
        print("3. Actualizar producto")
        print("4. Eliminar producto")
        print("0. Volver")
        op = input("Seleccione una opción: ")
        if op == "1":
            nombre = input("Nombre: ")
            descripcion = input("Descripción: ")
            categoria = input("Categoría: ")
            precio = input_float("Precio: ")
            stock = input_int("Stock: ")
            fecha_expiracion = input("Fecha expiración (YYYY-MM-DD, opcional): ") or None
            temporalidad = input("¿Es de temporada? (s/n): ").strip().lower() == "s"
            rebaja = input_float("Rebaja (0 si no aplica): ", allow_empty=True) or 0
            lista.registrar_producto(nombre, descripcion, categoria, precio, stock, fecha_expiracion, temporalidad, rebaja)
        elif op == "2":
            criterio = input("Buscar por (1) ID o (2) Nombre: ")
            if criterio == "1":
                idp = input_int("ID producto: ")
                res = lista.consultar_producto(id_producto=idp)
            else:
                nombre = input("Nombre producto: ")
                res = lista.consultar_producto(nombre=nombre)
            for p in res:
                print(vars(p))
        elif op == "3":
            idp = input_int("ID producto a actualizar: ")
            campo = input("Campo a actualizar (nombre, descripcion, categoria, precio, stock, fecha_expiracion, temporalidad, rebaja): ")
            valor = input("Nuevo valor: ")
            if campo in ["precio", "rebaja"]:
                try:
                    valor = float(valor)
                except ValueError:
                    print("Valor inválido para campo numérico.")
                    continue
            elif campo == "stock":
                try:
                    valor = int(valor)
                except ValueError:
                    print("Valor inválido para campo numérico.")
                    continue
            elif campo == "temporalidad":
                valor = valor.lower() == "true" or valor.lower() == "s"
            lista.actualizar_producto(idp, {campo: valor})
        elif op == "4":
            idp = input_int("ID producto a eliminar: ")
            lista.eliminar_producto(idp)
        elif op == "0":
            break

def menu_proveedores(lista):
    while True:
        print("\n--- Gestión de Proveedores ---")
        print("1. Registrar proveedor")
        print("2. Consultar proveedor")
        print("3. Actualizar proveedor")
        print("4. Eliminar proveedor")
        print("0. Volver")
        op = input("Seleccione una opción: ")
        if op == "1":
            nombre = input("Nombre: ")
            contacto = input("Contacto: ")
            direccion = input("Dirección: ")
            lista.registrar_proveedor(nombre, contacto, direccion)
        elif op == "2":
            idp = input_int("ID proveedor: ")
            p = lista.consultar_proveedor(idp)
            print(vars(p) if p else "No encontrado.")
        elif op == "3":
            idp = input_int("ID proveedor a actualizar: ")
            campo = input("Campo a actualizar (nombre, contacto, direccion): ")
            valor = input("Nuevo valor: ")
            lista.actualizar_proveedor(idp, {campo: valor})
        elif op == "4":
            idp = input_int("ID proveedor a eliminar: ")
            lista.eliminar_proveedor(idp)
        elif op == "0":
            break

def menu_clientes(lista):
    while True:
        print("\n--- Gestión de Clientes ---")
        print("1. Registrar cliente")
        print("2. Consultar cliente")
        print("3. Actualizar cliente")
        print("4. Eliminar cliente")
        print("0. Volver")
        op = input("Seleccione una opción: ")
        if op == "1":
            nombre = input("Nombre: ")
            contacto = input("Contacto: ")
            direccion = input("Dirección: ")
            tipo_cliente = input("Tipo cliente (minorista/mayorista): ")
            credito = input_float("Crédito (0 si no aplica): ", allow_empty=True) or 0
            lista.registrar_cliente(nombre, contacto, direccion, tipo_cliente, credito)
        elif op == "2":
            criterio = input("Buscar por (1) ID o (2) Nombre: ")
            if criterio == "1":
                idc = input_int("ID cliente: ")
                res = lista.consultar_cliente(id_cliente=idc)
            else:
                nombre = input("Nombre cliente: ")
                res = lista.consultar_cliente(nombre=nombre)
            for c in res:
                print(vars(c))
        elif op == "3":
            idc = input_int("ID cliente a actualizar: ")
            campo = input("Campo a actualizar (nombre, contacto, direccion, tipo_cliente, credito): ")
            valor = input("Nuevo valor: ")
            if campo == "credito":
                try:
                    valor = float(valor)
                except ValueError:
                    print("Valor inválido para campo numérico.")
                    continue
            lista.actualizar_cliente(idc, {campo: valor})
        elif op == "4":
            idc = input_int("ID cliente a eliminar: ")
            lista.eliminar_cliente(idc)
        elif op == "0":
            break

def menu_transacciones(lista):
    while True:
        print("\n--- Gestión de Transacciones ---")
        print("1. Registrar transacción")
        print("2. Consultar transacciones")
        print("3. Actualizar transacción")
        print("4. Eliminar transacción")
        print("0. Volver")
        op = input("Seleccione una opción: ")
        if op == "1":
            id_cliente = input_int("ID cliente: ")
            productos = input("Productos (separados por coma): ").split(",")
            productos = [p.strip() for p in productos]
            total = input_float("Total: ")
            fecha = input("Fecha (YYYY-MM-DD): ")
            tipo_pago = input("Tipo de pago: ")
            estado = input("Estado (pendiente/completada/cancelada): ")
            lista.registrar_transaccion(id_cliente, productos, total, fecha, tipo_pago, estado)
        elif op == "2":
            filtro = input("Filtrar por (1) Cliente, (2) Fecha, (3) Todos: ")
            if filtro == "1":
                idc = input_int("ID cliente: ")
                res = lista.consultar_transacciones(id_cliente=idc)
            elif filtro == "2":
                fecha = input("Fecha (YYYY-MM-DD): ")
                res = lista.consultar_transacciones(fecha=fecha)
            else:
                res = lista.consultar_transacciones()
            for t in res:
                print(vars(t))
        elif op == "3":
            idt = input_int("ID transacción a actualizar: ")
            campo = input("Campo a actualizar (estado, total, productos, tipo_pago, fecha): ")
            valor = input("Nuevo valor: ")
            if campo == "total":
                try:
                    valor = float(valor)
                except ValueError:
                    print("Valor inválido para campo numérico.")
                    continue
            elif campo == "productos":
                valor = [p.strip() for p in valor.split(",")]
            lista.actualizar_transaccion(idt, {campo: valor})
        elif op == "4":
            idt = input_int("ID transacción a eliminar: ")
            lista.eliminar_transaccion(idt)
        elif op == "0":
            break

def menu_movimientos(lista):
    while True:
        print("\n--- Gestión de Movimientos ---")
        print("1. Registrar movimiento")
        print("2. Consultar movimientos")
        print("3. Eliminar movimiento por ID transacción")
        print("0. Volver")
        op = input("Seleccione una opción: ")
        if op == "1":
            id_transaccion = input_int("ID transacción: ")
            fecha = input("Fecha (YYYY-MM-DD): ")
            tipo = input("Tipo (compra/venta): ")
            lista.registrar_movimiento(id_transaccion, fecha, tipo)
        elif op == "2":
            filtro = input("Filtrar por (1) Fecha, (2) Tipo, (3) Todos: ")
            if filtro == "1":
                fecha = input("Fecha (YYYY-MM-DD): ")
                res = lista.consultar_movimientos(fecha_consulta=fecha)
            elif filtro == "2":
                tipo = input("Tipo (compra/venta): ")
                res = lista.consultar_movimientos(tipo_consulta=tipo)
            else:
                res = lista.consultar_movimientos()
            for m in res:
                print(vars(m))
        elif op == "3":
            idt = input_int("ID transacción: ")
            lista.eliminar_movimiento_por_id_transaccion(idt)
        elif op == "0":
            break

def menu_rotaciones(modulo_rotaciones):
    while True:
        print("\n--- Gestión de Rotaciones ---")
        print("1. Verificar temporada de producto")
        print("2. Verificar rebaja de producto")
        print("3. Listar productos de temporada")
        print("4. Listar productos rebajados")
        print("5. Aplicar rebajas por expiración")
        print("0. Volver")
        op = input("Seleccione una opción: ")
        if op == "1":
            idp = input_int("ID producto: ")
            res = modulo_rotaciones.verificar_temporada(idp)
            print("Es de temporada" if res else "No es de temporada")
        elif op == "2":
            idp = input_int("ID producto: ")
            rebaja = modulo_rotaciones.verificar_rebaja(idp)
            print(f"Rebaja: {rebaja}")
        elif op == "3":
            lista = modulo_rotaciones.obtener_productos_temporada()
            for p in lista:
                print(vars(p))
        elif op == "4":
            lista = modulo_rotaciones.obtener_productos_rebajados()
            for p in lista:
                print(vars(p))
        elif op == "5":
            n = modulo_rotaciones.aplicar_rebajas_expiracion()
            print(f"Rebajas aplicadas a {n} producto(s).")
        elif op == "0":
            break

def main():
    productos = ListaProductos()
    proveedores = ListaProveedores()
    clientes = ListaClientes()
    transacciones = ListaTransacciones()
    movimientos = ListaMovimientos()
    rotaciones = ModuloRotaciones(productos)

    while True:
        menu_principal()
        op = input("Seleccione una opción: ")
        if op == "1":
            menu_productos(productos)
        elif op == "2":
            menu_proveedores(proveedores)
        elif op == "3":
            menu_clientes(clientes)
        elif op == "4":
            menu_transacciones(transacciones)
        elif op == "5":
            menu_movimientos(movimientos)
        elif op == "6":
            menu_rotaciones(rotaciones)
        elif op == "0":
            print("¡Hasta luego!")
            sys.exit()
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()
