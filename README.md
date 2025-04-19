# 🍎🥬 Proyecto-Final-ED1: Sistema de Gestión de Inventario para Tienda de Frutas y Verduras

Este es un proyecto final desarrollado en Python que implementa un **Sistema de Gestión de Inventario** para una tienda de frutas y verduras.
Permite controlar productos, stock, proveedores, clientes y ventas, incluyendo lógica de rotación de inventario por temporada y rebajas por fecha de expiración.

## 📦 Funcionalidades principales

- Registro, consulta, modificación y eliminación de productos.
- Gestión de stock, caducidad, temporalidad y rebajas.
- Módulo completo de proveedores y clientes.
- Registro y seguimiento de ventas (transacciones).
- Consulta de movimientos por tipo y fecha.
- Control de rotación de productos según temporada y vencimiento.

## 🧠 Arquitectura del sistema

El sistema está estructurado con clases y una base de datos SQLite. Las clases principales son:

### 🔸 Producto

- `id_producto`, `nombre`, `descripcion`, `categoria`, `precio`, `stock`, `fecha_expiracion`, `temporalidad`, `rebaja`
- Métodos: `registrar_producto()`, `actualizar_producto()`, `eliminar_producto()`, `consultar_producto()`, `aplicar_rebaja()`

### 🔸 Proveedor

- `id_proveedor`, `nombre`, `contacto`, `direccion`
- Métodos: `registrar_proveedor()`, `actualizar_proveedor()`, `eliminar_proveedor()`, `consultar_proveedor()`

### 🔸 Cliente

- `id_cliente`, `nombre`, `contacto`, `direccion`, `tipo_cliente`, `credito`
- Métodos: `registrar_cliente()`, `actualizar_cliente()`, `eliminar_cliente()`, `consultar_cliente()`

### 🔸 Transacción

- `id_transaccion`, `id_cliente`, `productos`, `total`, `fecha`, `tipo_pago`, `estado`
- Métodos: `registrar_transaccion()`, `actualizar_transaccion()`, `eliminar_transaccion()`, `consultar_transacciones()`

### 🔸 EstadoMovimiento

- `id_estado`, `id_transaccion`, `fecha`, `tipo`
- Métodos: `consultar_movimiento_por_fecha()`, `consultar_movimiento_por_tipo()`

### 🔸 RotaciónInventario

- `productos_temporada`, `productos_rebajados`
- Métodos: `verificar_temporada()`, `verificar_rebaja()`

## 🗃️ Estructura de la base de datos

Base de datos en SQLite con las siguientes tablas:

- **productos**
- **proveedores**
- **clientes**
- **transacciones**
- **estado_movimiento**
- **rotacion_inventario**

## 🔁 Flujo de operaciones

- **Inventario**: actualización de stock, rebajas automáticas y control de temporada.
- **Proveedores y clientes**: gestión completa con datos de contacto y tipo de cliente.
- **Transacciones**: registro de ventas con diferentes formas de pago.
- **Movimientos**: seguimiento por fecha o tipo (compra/venta).
- **Rotación**: control de productos temporales o por vencer.

## 🧠 Casos especiales

- **🎯 Productos de temporada**: solo disponibles en fechas específicas.
- **⚠️ Rebajas por expiración**: descuentos aplicados automáticamente.
- **📅 Consultas por fecha/tipo**: análisis de movimientos en el tiempo.

## 🛠️ Tecnologías utilizadas

- Python 3.x
- SQLite3
- Bibliotecas estándar (`datetime`, `json`, etc.)

## 🚀 Instalación y uso

1. Clona este repositorio:

   ```bash
   git clone https://github.com/a-nxwball/Proyecto-Final-ED1.git
   cd Proyecto-Final-ED1

   ```

```bash

````
