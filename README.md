# 🍎🥬 Proyecto Final (Estructura de Datos I): Sistema de Gestión de Inventario para Abarrotería

**Co-autores:**

- Aaron Newball (@a-nxwball)
- Alec Biruet (@Aleccito)
- Carlos Poveda (@CarlosPoveda822)
- Eimy Méndez (@EimyMendez)
- Esteban Dimas (@caleeeq)
- Irving Gutiérrez (@irving2109)

Sistema modular en Python para la gestión integral de inventario, ventas, clientes y proveedores en una abarrotería. Utiliza listas doblemente enlazadas para la gestión en memoria y sincronización bidireccional con SQLite para persistencia y consultas eficientes.

## Estructura General

El sistema está compuesto por módulos independientes que gestionan productos, proveedores, clientes, transacciones, movimientos y rotaciones. Cada módulo implementa una lista doblemente enlazada para operaciones eficientes en memoria y sincronización automática con la base de datos. Además, se emplea un árbol binario de búsqueda para la gestión de categorías de productos.

---

## Tipos de Estructuras de Datos (ED) y Funciones por Módulo

- **Productos:**  
  - *ED:* Lista doblemente enlazada de productos y árbol binario de búsqueda para categorías.
  - *Funciones:* Registrar, consultar, actualizar, eliminar productos; consultar por categoría; aplicar rebajas automáticas; mensajes de estado; sincronización con BD.

- **Proveedores:**  
  - *ED:* Lista doblemente enlazada de proveedores.
  - *Funciones:* Registrar, consultar, actualizar, eliminar proveedores; sincronización con BD.

- **Clientes:**  
  - *ED:* Lista doblemente enlazada de clientes.
  - *Funciones:* Registrar, consultar, actualizar, eliminar clientes; consultas por nombre o ID; resumen de movimientos; sincronización con BD.

- **Transacciones:**  
  - *ED:* Lista doblemente enlazada de transacciones.
  - *Funciones:* Registrar, consultar, actualizar, eliminar transacciones; reporte transaccional avanzado; sincronización con BD.

- **Movimientos:**  
  - *ED:* Lista doblemente enlazada de movimientos.
  - *Funciones:* Registrar, consultar, eliminar movimientos; reporte logístico; sincronización con BD.

- **Rotaciones:**  
  - *ED:* Referencia a la lista doblemente enlazada de productos.
  - *Funciones:* Verificar temporada/rebaja; listar productos de temporada/rebajados; aplicar rebajas automáticas.

---

## Arquitectura Modular y Persistencia

Cada módulo implementa su propia lista doblemente enlazada, que se sincroniza automáticamente con la base de datos SQLite. Al iniciar el sistema, los datos se cargan desde la base de datos a las listas enlazadas, y cualquier operación de registro, actualización o eliminación se refleja tanto en memoria como en la base de datos. Esto permite eficiencia en operaciones y persistencia de la información.

El árbol binario de categorías permite búsquedas rápidas y agrupación lógica de productos, facilitando consultas por categoría y operaciones de rebaja o temporada.

---

## Flujo Operacional y Manejo de Casos

1. **Gestión de Inventario:**  
   Los productos se gestionan y actualizan según stock, expiración y rebajas. Los productos de temporada se identifican y gestionan especialmente. El sistema emite mensajes automáticos de advertencia sobre expiración, rebajas y temporada.

2. **Gestión de Proveedores y Clientes:**  
   Permite mantener registros actualizados y relaciones con transacciones y movimientos. Las operaciones CRUD están sincronizadas con la base de datos.

3. **Gestión de Transacciones y Movimientos:**  
   Las ventas y compras se registran como transacciones, generando movimientos asociados para trazabilidad y consultas históricas. Los reportes permiten analizar ventas, compras, utilidades y saldos pendientes.

4. **Gestión de Rotaciones:**  
   Aplica lógica de rebajas automáticas a productos próximos a expirar y permite identificar productos de temporada o rebajados.

5. **Casos Especiales:**
   - Productos de temporada: Solo disponibles en ciertas épocas, identificados y gestionados por el sistema.
   - Rebajas automáticas: Descuentos aplicados a productos cercanos a su fecha de expiración o por temporada.
   - Consultas avanzadas: Inventario y movimientos pueden consultarse por fecha, tipo de transacción, cliente, proveedor o categoría.

---

## Simulación Semanal

- **Ubicación:** `simulaciones/simulacion_semana.py`
- **Propósito:** Simula una semana de operaciones en la tienda, incluyendo ventas diarias, reabastecimientos automáticos, aplicación de rebajas y generación de reportes.
- **Detalles:**
  - Inicializa productos, clientes y proveedores.
  - Simula ventas y compras diarias, ajustando stock y precios según rotación y margen.
  - Aplica rebajas automáticas a productos próximos a expirar o de temporada.
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
  - Sincronización automática con la base de datos en cada operación.

---

## Base de Datos

- **SQLite** con tablas:
  - `Productos`, `Proveedores`, `Clientes`, `Transacciones`, `Movimientos`, `Rotaciones`.
- Cada tabla refleja los atributos principales de cada módulo y mantiene integridad referencial mediante claves foráneas.
- La sincronización entre las listas enlazadas y la base de datos es automática y bidireccional.

---

## Uso

1. Clona el repositorio.
2. Ejecuta `App.py` para iniciar el sistema por consola.
3. Usa los menús interactivos para gestionar productos, clientes, proveedores, ventas y movimientos.
4. Ejecuta la simulación semanal con `simulaciones/simulacion_semana.py` para pruebas automáticas y generación de reportes.

## Requisitos

- Python 3.x
- SQLite3
- SimPy 4.x

---
