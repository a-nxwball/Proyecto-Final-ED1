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

El sistema está estructurado en módulos de Python dentro de la carpeta `app`:

### Modulo de Productos

- Clases: `Productos`, `ListaProductos`

### Modulo de Proveedores

- Clases: `Proveedor`, `ListaProveedores`

### Modulo de Clientes

- Clases: `Cliente`, `ListaClientes`

### Modulo de Transacciones

- Clases: `Transaccion`, `ListaTransacciones`

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
