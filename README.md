# 🍎🥬 Proyecto Final (Estructura de Datos I): Sistema de Gestión de Inventario para Abarrotería

**Co-autores:**

- Aaron Newball  
- Alec Biruet
- Carlos Poveda
- Eimy Méndez
- Irving Gutiérrez
- Esteban Dimas

Sistema modular en Python para la gestión integral de inventario, ventas, clientes y proveedores en una Abarrotería. Utiliza listas doblemente enlazadas para la gestión en memoria y sincronización con SQLite para persistencia.

## Estructura General

El sistema está compuesto por módulos independientes que gestionan productos, proveedores, clientes, transacciones, movimientos y rotaciones. Cada módulo implementa una lista doblemente enlazada para operaciones eficientes y sincronización automática con la base de datos.

---

## Tipos de Estructuras de Datos (ED) y Funciones por Módulo

- **Productos:**  
  - *ED:* Lista doblemente enlazada de productos y árbol binario de búsqueda para categorías.
  - *Funciones:* Registrar, consultar, actualizar, eliminar productos; consultar por categoría; aplicar rebajas automáticas; mensajes de estado.

- **Proveedores:**  
  - *ED:* Lista doblemente enlazada de proveedores.
  - *Funciones:* Registrar, consultar, actualizar, eliminar proveedores.

- **Clientes:**  
  - *ED:* Lista doblemente enlazada de clientes.
  - *Funciones:* Registrar, consultar, actualizar, eliminar clientes; consultas por nombre o ID; resumen de movimientos.

- **Transacciones:**  
  - *ED:* Lista doblemente enlazada de transacciones.
  - *Funciones:* Registrar, consultar, actualizar, eliminar transacciones; reporte transaccional avanzado.

- **Movimientos:**  
  - *ED:* Lista doblemente enlazada de movimientos.
  - *Funciones:* Registrar, consultar, eliminar movimientos; reporte logístico.

- **Rotaciones:**  
  - *ED:* Referencia a la lista doblemente enlazada de productos.
  - *Funciones:* Verificar temporada/rebaja; listar productos de temporada/rebajados; aplicar rebajas automáticas.

---

### Módulos Principales

### Módulo Productos (`app/ModuloProductos.py`)

- **Atributos principales:**  
  - Lista doblemente enlazada de productos (`raiz`)
  - Árbol de categorías (`arbol_categorias`)
- **Funciones clave:**  
  - Registrar, consultar, actualizar y eliminar productos
  - Consultar productos por categoría
  - Aplicar rebajas automáticas por expiración o temporada
  - Mensajes automáticos de estado (expiración, rebaja, temporada)

### Módulo Proveedores (`app/ModuloProveedores.py`)

- **Atributos principales:**  
  - Lista doblemente enlazada de proveedores (`raiz`)
- **Funciones clave:**  
  - Registrar, consultar, actualizar y eliminar proveedores

### Módulo Clientes (`app/ModuloClientes.py`)

- **Atributos principales:**  
  - Lista doblemente enlazada de clientes (`raiz`)
- **Funciones clave:**  
  - Registrar, consultar, actualizar y eliminar clientes
  - Consultas por nombre o ID
  - Resumen de movimientos por cliente

### Módulo Transacciones (`app/ModuloTransacciones.py`)

- **Atributos principales:**  
  - Lista doblemente enlazada de transacciones (`raiz`)
- **Funciones clave:**  
  - Registrar, consultar, actualizar y eliminar transacciones
  - Reporte transaccional avanzado (ventas, compras, utilidades, pagos, saldos)

### Módulo Movimientos (`app/ModuloMovimientos.py`)

- **Atributos principales:**  
  - Lista doblemente enlazada de movimientos (`raiz`)
- **Funciones clave:**  
  - Registrar, consultar y eliminar movimientos
  - Reporte logístico (rotación, entradas/salidas, alertas de stock)

### Módulo Rotaciones (`app/ModuloRotaciones.py`)

- **Atributos principales:**  
  - Referencia a la lista de productos
- **Funciones clave:**  
  - Verificar si un producto es de temporada o tiene rebaja
  - Listar productos de temporada o rebajados
  - Aplicar rebajas automáticas por expiración o temporada

---

## Flujo Operacional y Manejo de Casos

1. **Gestión de Inventario:**  
   Los productos se gestionan y actualizan según stock, expiración y rebajas. Los productos de temporada se identifican y gestionan especialmente.
2. **Gestión de Proveedores y Clientes:**  
   Permite mantener registros actualizados y relaciones con transacciones y movimientos.
3. **Gestión de Transacciones y Movimientos:**  
   Las ventas y compras se registran como transacciones, generando movimientos asociados para trazabilidad y consultas históricas.
4. **Gestión de Rotaciones:**  
   Aplica lógica de rebajas automáticas a productos próximos a expirar y permite identificar productos de temporada.
5. **Casos Especiales:**
   - Productos de temporada: Solo disponibles en ciertas épocas, identificados y gestionados por el sistema.
   - Rebajas automáticas: Descuentos aplicados a productos cercanos a su fecha de expiración.
   - Consultas avanzadas: Inventario y movimientos pueden consultarse por fecha y tipo de transacción.

---

## Simulación Semanal

- **Ubicación:** `simulaciones/simulacion_semana.py`
- **Propósito:** Simula una semana de operaciones en la tienda, incluyendo ventas diarias, reabastecimientos automáticos, aplicación de rebajas y generación de reportes.
- **Detalles:**
  - Inicializa productos, clientes y proveedores.
  - Simula ventas y compras diarias, ajustando stock y precios según rotación y margen.
  - Aplica rebajas automáticas a productos próximos a expirar.
  - Genera reportes finales: transaccional, logístico, productos de temporada y rebajados.
  - Permite reiniciar la base de datos y limpiar cachés para pruebas repetibles.

---

## Gestión del Sistema por CLI

- **Archivo principal:** `App.py`
- **Menús interactivos:**  
  - Productos: Registrar, consultar, actualizar, eliminar, consultar por categoría.
  - Proveedores: Registrar, consultar, actualizar, eliminar.
  - Clientes: Registrar, consultar, actualizar, eliminar.
  - Transacciones: Registrar, consultar, actualizar, eliminar.
  - Movimientos: Registrar, consultar, eliminar por transacción.
  - Rotaciones: Verificar temporada, rebaja, listar productos de temporada/rebajados, aplicar rebajas por expiración.
- **Detalles:**
  - Navegación por menús numéricos.
  - Validación de entradas y mensajes automáticos de estado.
  - Consultas avanzadas y reportes desde la CLI.
  - Sincronización automática con la base de datos.

---

## Base de Datos

- **SQLite** con tablas:
  - `Productos`, `Proveedores`, `Clientes`, `Transacciones`, `Movimientos`, `Rotaciones`.
- Cada tabla refleja los atributos principales de cada módulo y mantiene integridad referencial mediante claves foráneas.

---

## Uso

1. Clona el repositorio.
2. Ejecuta `App.py` para iniciar el sistema por consola.
3. Usa los menús interactivos para gestionar productos, clientes, proveedores, ventas y movimientos.
4. Ejecuta la simulación semanal con `simulaciones/simulacion_semana.py` para pruebas automáticas.

## Requisitos

- Python 3.x
- SQLite3
- SimPy 4.x

---
