# 🍎🥬 Proyecto-Final-ED1: Sistema de Gestión de Inventario para Tienda de Frutas y Verduras

Este es un proyecto final desarrollado en Python que implementa un **Sistema de Gestión de Inventario** para una tienda de frutas y verduras.
Permite controlar productos, stock, proveedores, clientes y ventas e incluyendo lógica de rotación inventario.

## 📦 Funcionalidades principales

- Sistema modular con lógica basada en estructuras de datos.
- Almacenamiento de los datos de manera sincronizada con la librería SQLite.
- Funciones de crear, leer, actualizar y eliminar los datos de cada módulo.
- 

## 🧠 Arquitectura del sistema

El sistema está estructurado en módulos de Python dentro de la carpeta `app`:

### Modulo de Productos

- Clases: `Producto`, `ListaProductos`

### Modulo de Proveedores

- Clases: `Proveedor`, `ListaProveedores`

### Modulo de Clientes

- Clases: `Cliente`, `ListaClientes`

### Modulo de Transacciones

- Clases: `Transaccion`, `ListaTransacciones`

## 🗃️ Estructura de la base de datos

Base de datos en SQLite con las siguientes tablas:

- **producto**
- **proveedor**
- **cliente**
- **transaccion**
- **estado_movimiento**
- **rotacion_inventario**

## 🔁 Flujo de operaciones

- **Gestión de Inventario**: Actualizacion de stock automatica y manejo de rebajas por temporalidad y expiración.
- **Gestión de Proveedores y Clientes**: gestión completa con datos de contacto y tipo de cliente.
- **Gestión de Transacciones**: Registro, manejo y seguimiento del flujo de ventas.
- **Rotación**: "Clase-Método" para el control de temporalidad y expiración.
- **Movimientos**: "Clase-Método" para el seguimiento de los estados de una transacción.

## 🧠 Casos especiales simuados

- **🎯 Productos de temporada**: Rebajas o aumento de precio dependiendo de la temporada.
- **⚠️ Rebajas por expiración**: Descuentos automáticos por productos por expirar.

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
