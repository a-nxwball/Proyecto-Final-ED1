import os
import sys
# Añadir directorio padre para importar módulos de app y bd
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from app.ModuloTransacciones import ListaTransacciones # Transaccion ya no se necesita instanciar aquí directamente
from bd.BDSQLite import crear_tablas, conectar_db # Para limpiar/preparar la BD para pruebas

def limpiar_bd():
    # Función auxiliar para asegurar una BD limpia para las pruebas
    # ¡PRECAUCIÓN! Esto borrará los datos existentes. Usar solo en entorno de prueba.
    print("\n--- Limpiando y recreando tablas para la prueba ---")
    crear_tablas() # Vuelve a crear las tablas (borra las anteriores)
    print("--- Tablas recreadas ---")

def main():
    # Limpiar la BD antes de empezar la prueba
    limpiar_bd()

    def imprimir_transacciones(transacciones):
        if not transacciones:
            print("No hay transacciones para mostrar.")
            return
        for t in transacciones:
            # Asegurarse de que t es un objeto Transaccion con los atributos esperados
            if hasattr(t, 'id_transaccion'):
                 print(f"ID: {t.id_transaccion}, Cliente: {t.id_cliente}, Productos: {t.productos}, Total: {t.total}, Fecha: {t.fecha}, Estado: {t.estado}")
            else:
                 print(f"Elemento inesperado en la lista: {t}")

    lista = ListaTransacciones() # Ahora carga desde la BD (que debería estar vacía)

    # Registrar transacciones usando los nuevos parámetros del método
    print("\nRegistrando transacciones...")
    t1_obj = lista.registrar_transaccion(101, ['prod1', 'prod2'], 100.0, '2024-06-01', 'efectivo', 'completada')
    t2_obj = lista.registrar_transaccion(102, ['prod3'], 50.0, '2024-06-02', 'tarjeta', 'pendiente')
    t3_obj = lista.registrar_transaccion(101, ['prod4'], 75.0, '2024-06-01', 'credito', 'completada')

    # Verificar si se registraron correctamente (los IDs serán asignados por la BD, probablemente 1, 2, 3)
    if t1_obj: print(f"Transacción 1 registrada con ID: {t1_obj.id_transaccion}")
    if t2_obj: print(f"Transacción 2 registrada con ID: {t2_obj.id_transaccion}")
    if t3_obj: print(f"Transacción 3 registrada con ID: {t3_obj.id_transaccion}")

    # Obtener IDs reales asignados por la BD (asumiendo que son 1, 2, 3 si la BD estaba vacía)
    # Es más robusto buscar por otros criterios o usar los objetos devueltos si no son None
    id_t1 = t1_obj.id_transaccion if t1_obj else None
    id_t2 = t2_obj.id_transaccion if t2_obj else None
    id_t3 = t3_obj.id_transaccion if t3_obj else None

    print("\nTodas las transacciones después de registrar:")
    imprimir_transacciones(lista.consultar_transacciones())

    if id_t2:
        print(f"\nActualizando transacción ID {id_t2}...")
        actualizado = lista.actualizar_transaccion(id_t2, {'estado': 'completada', 'total': 55.0})
        if actualizado:
            print(f"Transacción {id_t2} actualizada.")
            print("\nTransacciones del cliente 102 después de actualizar:")
            imprimir_transacciones(lista.consultar_transacciones(id_cliente=102))
        else:
            print(f"Error al actualizar transacción {id_t2}.")

    if id_t1:
        print(f"\nEliminando transacción ID {id_t1}...")
        eliminado = lista.eliminar_transaccion(id_t1)
        if eliminado:
            print(f"Transacción {id_t1} eliminada.")
            print("\nTodas las transacciones después de eliminar:")
            imprimir_transacciones(lista.consultar_transacciones())
        else:
             print(f"Error al eliminar transacción {id_t1}.")


    print("\nTransacciones restantes del cliente 101:")
    imprimir_transacciones(lista.consultar_transacciones(id_cliente=101))

    print("\nTransacciones restantes del 2024-06-01:")
    imprimir_transacciones(lista.consultar_transacciones(fecha='2024-06-01'))

if __name__ == "__main__":
    main()