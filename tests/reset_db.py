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

def limpiar_cache_pycache(root_dir):
    """
    Elimina todos los directorios __pycache__ y archivos .pyc en el proyecto.
    """
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Eliminar directorios __pycache__
        if "__pycache__" in dirnames:
            pycache_path = os.path.join(dirpath, "__pycache__")
            try:
                import shutil
                shutil.rmtree(pycache_path)
                print(f"Eliminado: {pycache_path}")
            except Exception as e:
                print(f"Error al eliminar {pycache_path}: {e}")
        # Eliminar archivos .pyc
        for filename in filenames:
            if filename.endswith(".pyc"):
                pyc_path = os.path.join(dirpath, filename)
                try:
                    os.remove(pyc_path)
                    print(f"Eliminado: {pyc_path}")
                except Exception as e:
                    print(f"Error al eliminar {pyc_path}: {e}")

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
    # Limpiar caché de Python
    print("Eliminando cachés (__pycache__ y .pyc)...")
    limpiar_cache_pycache(BASE_DIR)
    print("Limpieza de caché completada.")

if __name__ == "__main__":
    resetear_bd()
