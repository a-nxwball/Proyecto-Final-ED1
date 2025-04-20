import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "bd", "TiendaFrutasVerduras.db")

TABLAS = [
    "Rotaciones",
    "Movimientos",
    "Transacciones",
    "Clientes",
    "Proveedores",
    "Productos"
]

def resetear_bd():
    if not os.path.exists(DB_PATH):
        print("No existe la base de datos:", DB_PATH)
        return
    conexion = sqlite3.connect(DB_PATH)
    try:
        cursor = conexion.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF")
        for tabla in TABLAS:
            cursor.execute(f"DELETE FROM {tabla}")
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{tabla}'")
        conexion.commit()
        print("Base de datos limpiada y autoincrementos reiniciados.")
    except Exception as e:
        print("Error al limpiar la base de datos:", e)
        conexion.rollback()
    finally:
        conexion.close()

if __name__ == "__main__":
    resetear_bd()
