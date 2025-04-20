import os
import sqlite3

BASE_DIR = os.path.dirname(__file__)
nombre_db = os.path.join(BASE_DIR, 'Abarrotería.db')

# Función para conectar a la base de datos SQLite y devolver la conexión
def conectar_db():
    try:
        conexion = sqlite3.connect(nombre_db)
        return conexion
    except sqlite3.Error as e:
        print(f"No se puede conectar a la BD: {e}")
        return None

# Función para crear las tablas necesarias en la base de datos
def crear_tablas():
    conexion = conectar_db()
    if conexion:
        cursor = conexion.cursor()

        cursor.execute("PRAGMA foreign_keys = ON")
        
        cursor.execute("DROP TABLE IF EXISTS Rotaciones")
        cursor.execute("DROP TABLE IF EXISTS Movimientos")
        cursor.execute("DROP TABLE IF EXISTS Transacciones")
        cursor.execute("DROP TABLE IF EXISTS Clientes")
        cursor.execute("DROP TABLE IF EXISTS Proveedores")
        cursor.execute("DROP TABLE IF EXISTS Productos")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Productos (
                id_producto INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                categoria TEXT NOT NULL,
                precio REAL NOT NULL CHECK(precio >= 0),
                stock INTEGER NOT NULL CHECK(stock >= 0),
                fecha_expiracion DATE,
                temporalidad BOOLEAN NOT NULL DEFAULT 0,
                rebaja REAL NOT NULL DEFAULT 0,
                id_proveedor INTEGER,
                FOREIGN KEY (id_proveedor) REFERENCES Proveedores(id_proveedor) ON DELETE SET NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Proveedores (
                id_proveedor INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                nombre TEXT NOT NULL,
                contacto TEXT,
                direccion TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Clientes (
                id_cliente INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                nombre TEXT NOT NULL,
                contacto TEXT,
                direccion TEXT,
                tipo_cliente TEXT NOT NULL,
                credito REAL NOT NULL DEFAULT 0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Transacciones (
                id_transaccion INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                id_cliente INTEGER,
                id_proveedor INTEGER,
                productos TEXT NOT NULL,
                total REAL NOT NULL CHECK(total >= 0),
                fecha DATE NOT NULL,
                tipo_pago TEXT NOT NULL,
                estado TEXT NOT NULL,
                FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente) ON DELETE CASCADE,
                FOREIGN KEY (id_proveedor) REFERENCES Proveedores(id_proveedor) ON DELETE SET NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Movimientos (
                id_estado INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                id_transaccion INTEGER NOT NULL,
                fecha DATE NOT NULL,
                tipo TEXT NOT NULL,
                FOREIGN KEY (id_transaccion) REFERENCES Transacciones(id_transaccion) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Rotaciones (
                id_producto INTEGER NOT NULL,
                fecha_inicio DATE NOT NULL,
                fecha_fin DATE NOT NULL,
                tipo TEXT NOT NULL,
                FOREIGN KEY (id_producto) REFERENCES Productos(id_producto) ON DELETE CASCADE
            )
        """)

        conexion.commit()
        print("Tablas creadas exitosamente.")
        conexion.close()

if __name__ == "__main__":
    crear_tablas()
