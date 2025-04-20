# 🍎🥬 Proyecto-Final-ED1: Sistema de Gestión de Inventario para Tienda de Frutas y Verduras

Sistema modular en Python para la gestión integral de inventario, ventas, clientes y proveedores en una tienda de frutas y verduras. Utiliza listas doblemente enlazadas para la gestión en memoria y sincronización con SQLite para persistencia.

## Estructura General

El sistema está compuesto por módulos independientes que gestionan productos, proveedores, clientes, transacciones, movimientos y rotaciones. Cada módulo implementa una lista doblemente enlazada para operaciones eficientes y sincronización automática con la base de datos.

### Módulos y Funcionalidades

- **Productos**
  - Registro, consulta, actualización y eliminación de productos.
  - Control de stock, expiración, temporalidad y rebajas automáticas.
  - Atributos principales: `id_producto`, `nombre`, `descripcion`, `categoria`, `precio`, `stock`, `fecha_expiracion`, `temporalidad`, `rebaja`.
  - Funciones clave: `registrar_producto`, `actualizar_producto`, `eliminar_producto`, `consultar_producto`, `aplicar_rebaja`.

- **Proveedores**
  - Gestión de proveedores: registro, consulta, actualización y eliminación.
  - Atributos: `id_proveedor`, `nombre`, `contacto`, `direccion`.

- **Clientes**
  - Registro y gestión de clientes, tipos (minorista/mayorista) y crédito.
  - Atributos: `id_cliente`, `nombre`, `contacto`, `direccion`, `tipo_cliente`, `credito`.

- **Transacciones**
  - Registro y consulta de ventas, actualización y eliminación.
  - Atributos: `id_transaccion`, `id_cliente`, `productos`, `total`, `fecha`, `tipo_pago`, `estado`.

- **Movimientos**
  - Registro y consulta de movimientos de inventario (ventas/compras) por fecha y tipo.
  - Atributos: `id_estado`, `id_transaccion`, `fecha`, `tipo`.

- **Rotaciones**
  - Lógica de temporada y rebajas automáticas por expiración.
  - Funciones: `verificar_temporada`, `verificar_rebaja`, `obtener_productos_temporada`, `obtener_productos_rebajados`, `aplicar_rebajas_expiracion`.

## Base de Datos

- **SQLite** con tablas:
  - `Productos`, `Proveedores`, `Clientes`, `Transacciones`, `Movimientos`, `Rotaciones`.
- Cada tabla refleja los atributos principales de cada módulo y mantiene integridad referencial mediante claves foráneas.

## Flujo de Operaciones

1. **Gestión de Inventario:**  
   Los productos se gestionan y actualizan según stock, expiración y rebajas. Los productos de temporada se manejan especialmente para su disponibilidad.

2. **Gestión de Proveedores y Clientes:**  
   Permite mantener registros actualizados y relaciones con transacciones y movimientos.

3. **Gestión de Transacciones y Movimientos:**  
   Las ventas y compras se registran como transacciones, generando movimientos asociados para trazabilidad y consultas históricas.

4. **Gestión de Rotaciones:**  
   Aplica lógica de rebajas automáticas a productos próximos a expirar y permite identificar productos de temporada.

## Casos Especiales

- **Productos de temporada:**  
  Solo disponibles en ciertas épocas, identificados y gestionados por el sistema.
- **Rebajas automáticas:**  
  Descuentos aplicados a productos cercanos a su fecha de expiración.
- **Consultas avanzadas:**  
  Inventario y movimientos pueden consultarse por fecha y tipo de transacción.

## Uso

1. Clona el repositorio.
2. Ejecuta `App.py` para iniciar el sistema por consola.
3. Usa los menús interactivos para gestionar productos, clientes, proveedores, ventas y movimientos.

## Requisitos

- Python 3.x
- SQLite3

---
