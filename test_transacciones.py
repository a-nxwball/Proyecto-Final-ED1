from Clase_Transacción import Transaccion, ListaTransacciones

def __main__():
    def imprimir_transacciones(transacciones):
        for t in transacciones:
            print(f"ID: {t.id_transaccion}, Cliente: {t.id_cliente}, Total: {t.total}, Fecha: {t.fecha}, Estado: {t.estado}")
            
    # Crear lista de transacciones
    lista = ListaTransacciones()

    # Registrar transacciones
    t1 = Transaccion(1, 101, ['prod1', 'prod2'], 100.0, '2024-06-01', 'efectivo', 'completada')
    t2 = Transaccion(2, 102, ['prod3'], 50.0, '2024-06-02', 'tarjeta', 'pendiente')
    t3 = Transaccion(3, 101, ['prod4'], 75.0, '2024-06-01', 'credito', 'completada')

    lista.registrar_transaccion(t1)
    lista.registrar_transaccion(t2)
    lista.registrar_transaccion(t3)

    print("Todas las transacciones:")
    imprimir_transacciones(lista.consultar_transacciones())

    # Actualizar una transacción
    lista.actualizar_transaccion(2, {'estado': 'completada', 'total': 55.0})
    print("\nTransacción 2 actualizada:")
    imprimir_transacciones(lista.consultar_transacciones(id_cliente=102))

    # Eliminar una transacción
    lista.eliminar_transaccion(1)
    print("\nDespués de eliminar transacción 1:")
    imprimir_transacciones(lista.consultar_transacciones())

    # Consultar por cliente
    print("\nTransacciones del cliente 101:")
    imprimir_transacciones(lista.consultar_transacciones(id_cliente=101))

    # Consultar por fecha
    print("\nTransacciones del 2024-06-01:")
    imprimir_transacciones(lista.consultar_transacciones(fecha='2024-06-01'))
    
if __name__ == "__main__":
    __main__()