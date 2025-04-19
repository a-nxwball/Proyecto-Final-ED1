import sqlite3

nombre_db = 'TiendaFrutasVerduras.db'

def conectar_db():
    """Conectar a SQLite."""
    try:
        conexion = sqlite3.connect(nombre_db)
        return conexion
    except sqlite3.Error as e:
        print(f"No se puede conectar a la BD: {e}")
        return None

def crear_tablas():
    conexion = conectar_db()
    if conexion:
        cursor = conexion.cursor()

        # Habilitar comprobación de claves foráneas
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Opcional: limpiar tablas antiguas antes de recrear
        cursor.execute("DROP TABLE IF EXISTS Rotaciones")
        cursor.execute("DROP TABLE IF EXISTS Movimientos")
        cursor.execute("DROP TABLE IF EXISTS Transacciones")
        cursor.execute("DROP TABLE IF EXISTS Clientes")
        cursor.execute("DROP TABLE IF EXISTS Proveedores")
        cursor.execute("DROP TABLE IF EXISTS Productos")

        # Tabla Productos
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
                rebaja REAL NOT NULL DEFAULT 0
            )
        """)

        # Tabla Proveedores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Proveedores (
                id_proveedor INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                nombre TEXT NOT NULL,
                contacto TEXT,
                direccion TEXT
            )
        """)

        # Tabla Clientes
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

        # Tabla Transacciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Transacciones (
                id_transaccion INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                id_cliente INTEGER NOT NULL,
                productos TEXT NOT NULL,
                total REAL NOT NULL CHECK(total >= 0),
                fecha DATE NOT NULL,
                tipo_pago TEXT NOT NULL,
                estado TEXT NOT NULL,
                FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente) ON DELETE CASCADE
            )
        """)

        # Tabla Movimientos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Movimientos (
                id_estado INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                id_transaccion INTEGER NOT NULL,
                fecha DATE NOT NULL,
                tipo TEXT NOT NULL,
                FOREIGN KEY (id_transaccion) REFERENCES Transacciones(id_transaccion) ON DELETE CASCADE
            )
        """)

        # Tabla Rotaciones
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
