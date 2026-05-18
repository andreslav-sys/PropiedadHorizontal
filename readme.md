Sistema de Administración de Propiedad Horizontal
Versión 2 — API REST con Flask + JWT
> \*\*Rama:\*\* `v2-api` | \*\*Base:\*\* rama `main`
> \*\*GitHub:\*\* https://github.com/andreslav-sys/PropiedadHorizontal
---
¿Qué es este proyecto?
Sistema de administración de propiedad horizontal desarrollado en Python,
que expone los datos a través de una API REST con autenticación segura
mediante tokens JWT (JSON Web Token).
Esta versión es una mejora directa sobre la rama `main`, que contiene
el código base con operaciones CRUD directas a la base de datos.
---
Filosofía de Software Libre
Este proyecto aplica los principios de la Free Software Foundation (FSF):
Libertad 0 — Cualquier persona puede ejecutar este programa para cualquier propósito.
Libertad 1 — El código fuente está disponible para ser estudiado y modificado.
Libertad 2 — Las mejoras pueden redistribuirse libremente (como se hace en esta rama).
Libertad 3 — Las versiones modificadas pueden publicarse para beneficio de la comunidad.
La relación entre `main` → `v2-api` demuestra en la práctica cómo el software
libre permite tomar un programa existente, mejorarlo y publicar esa mejora
de forma transparente y trazable.
---
Diferencias con la versión base (rama main)
Característica	`main` (v1)	`v2-api` (v2)
Acceso a datos	Directo desde Python	Via API REST (HTTP)
Autenticación	No tiene	JWT con algoritmo HS512
Encriptación de token	No tiene	HMAC-SHA512
Endpoints HTTP	No tiene	GET, POST, PUT, DELETE
Stored Procedure via API	No tiene	✅ Endpoint dedicado
Clase Autenticacion	No tiene	✅ Separada
Serialización JSON	No tiene	✅ Método ToDict()
Validación centralizada	No tiene	✅ ValidarEntrada()
Consumible desde app web/móvil	No	Sí
---
Tecnologías utilizadas
Python 3 — Lenguaje principal (FSF avalado)
MySQL — Gestor de base de datos libre
Flask — Framework web ligero para Python
PyJWT — Librería para tokens JWT
pyodbc — Conector ODBC para MySQL
---
Instalación
```bash
py -m pip install pyodbc
py -m pip install Flask
py -m pip install PyJWT
```
---
Ejecutar
```bash
py main.py
```
El servidor inicia en: `http://localhost:4040`
---
Endpoints disponibles
1. Obtener Token
```
GET http://localhost:4040/api/token/generar
```
Respuesta:
```json
{
  "Token": "eyJ...",
  "Respuesta": "OK",
  "Fecha": "2026-05-18 10:00:00"
}
```
2. Obtener propietarios
```
GET http://localhost:4040/api/propietarios/{"Token":"eyJ..."}
```
3. Obtener propietarios via Stored Procedure
```
GET http://localhost:4040/api/propietarios/sp/{"Token":"eyJ..."}
```
4. Insertar propietario
```
POST http://localhost:4040/api/propietarios/{"Token":"eyJ...","apartamento\_id":1,"cedula":"123","nombre":"Juan","telefono":"300...","email":"j@mail.com"}
```
5. Actualizar propietario
```
PUT http://localhost:4040/api/propietarios/{"Token":"eyJ...","id":1,"nombre":"Nuevo Nombre",...}
```
6. Eliminar propietario
```
DELETE http://localhost:4040/api/propietarios/{"Token":"eyJ...","id":5}
```
---
Estructura del proyecto
```
PropiedadHorizontal/
├── main      ← versión base (CRUD directo)
└── v2-api    ← esta rama (API REST + JWT)
    ├── main.py       — API REST completa
    ├── Script.sql    — Base de datos db\_ph (15 tablas)
    ├── README.md     — Este archivo
    └── .gitignore
```
---
Base de datos — 15 tablas
`conjuntos` · `torres` · `apartamentos` · `propietarios` · `cuotas` ·
`pagos` · `areas\_comunes` · `reservas` · `asambleas` · `asistencias` ·
`empleados` · `novedades` · `proveedores` · `contratos` · `vehiculos`
---
Autor
Andrés — Instituto Tecnológico Metropolitano (ITM)
Ingeniería — Integración de Software Libre