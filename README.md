📦 Gestión de Inventario API

API REST para la gestión de inventario desarrollada con Python y FastAPI.

El proyecto implementa autenticación mediante JWT, autorización basada en roles, gestión de usuarios, categorías y productos, movimientos de stock, historial, paginación, filtros, soft delete, manejo de errores, logging y migraciones de base de datos con Alembic.

La aplicación está preparada para ejecutarse tanto en un entorno local como mediante Docker Compose con PostgreSQL.

---

🚀 Tecnologías

- Python 3.13
- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL
- SQLite en memoria para tests
- JWT
- pwdlib + Argon2
- Pytest
- Docker
- Docker Compose
- Alembic
- Uvicorn

---

📋 Características

🔐 Autenticación y usuarios

- Registro de usuarios
- Login mediante OAuth2 Password Flow
- Autenticación mediante JWT
- Hash seguro de contraseñas utilizando Argon2
- Validación de tokens
- Tokens con fecha de expiración
- Endpoint "/auth/me"
- Usuarios activos e inactivos
- Roles:
  - "user"
  - "admin"
- Dependencias para autenticación y autorización
- Protección de endpoints según rol

El registro público únicamente permite crear usuarios con:

role=user

No es posible registrarse directamente como administrador.

---

👑 Administrador inicial

El proyecto incluye un mecanismo para crear automáticamente el administrador inicial.

Script:

app/scripts/create_admin.py

La lógica utiliza el servicio existente:

app/services/admin.py

Las credenciales se proporcionan mediante variables de entorno:

ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@inventory.local
ADMIN_PASSWORD=change_this_admin_password

Cuando la aplicación se ejecuta mediante Docker, el "entrypoint.sh" ejecuta:

python -m app.scripts.create_admin

El proceso comprueba si el administrador ya existe antes de crearlo.

---

🗂️ Categorías

CRUD completo de categorías.

Incluye:

- Crear categoría
- Consultar categorías
- Consultar categoría individual
- Actualizar categoría
- Eliminación lógica mediante "is_active"
- Ocultamiento de categorías eliminadas
- Protección de operaciones administrativas
- Validación de categorías activas

Las categorías eliminadas mediante soft delete no aparecen en los listados normales ni pueden consultarse como recursos activos.

---

📦 Productos

CRUD completo de productos.

Incluye:

- Crear producto
- Consultar productos
- Consultar producto individual
- Actualizar producto
- Eliminación lógica
- Relación con categorías mediante SQLAlchemy
- Validación de categoría existente y activa
- Validación de precio
- Validación de stock
- Protección de operaciones administrativas
- Filtros
- Paginación

Las operaciones de escritura sobre productos requieren permisos de administrador.

El stock no puede modificarse directamente mediante la actualización normal del producto.

Los cambios de stock se realizan mediante movimientos de inventario.

---

📊 Paginación y filtros

Los endpoints de consulta permiten trabajar con grandes cantidades de información mediante:

- Paginación
- Parámetros de consulta
- Filtros sobre productos
- Listados únicamente de recursos activos

Esto permite mantener respuestas controladas y facilitar el consumo de la API.

---

🔄 Movimientos de stock

El proyecto incorpora un sistema de movimientos de inventario.

Modelo:

StockMovement

Tipos de movimiento:

entrada
salida

Entrada

Una entrada incrementa el stock del producto.

Salida

Una salida disminuye el stock.

El sistema valida:

- Producto existente
- Tipo de movimiento válido
- Cantidad positiva
- Cantidad diferente de cero
- Stock suficiente para realizar una salida
- Usuario autorizado

La creación de movimientos requiere permisos de administrador.

---

📜 Historial de movimientos

Los movimientos quedan registrados y pueden consultarse para mantener un historial de las modificaciones de stock.

Esto permite conocer las entradas y salidas realizadas sobre los productos.

---

🗄️ Base de datos

En desarrollo y producción mediante Docker se utiliza:

PostgreSQL

Para los tests se utiliza:

SQLite en memoria

La aplicación utiliza:

SQLAlchemy

como ORM.

Las relaciones entre usuarios, categorías, productos y movimientos de stock están definidas mediante modelos SQLAlchemy.

---

🔄 Migraciones con Alembic

Las modificaciones del esquema de base de datos se gestionan mediante Alembic.

La migración inicial crea las tablas necesarias para:

user
category
product
stock_movement
alembic_version

La migración actual se encuentra en:

alembic/versions/

Al iniciar el contenedor de la API, el "entrypoint.sh" ejecuta automáticamente:

alembic upgrade head

Esto permite que las migraciones pendientes se apliquen antes de iniciar FastAPI.

---

🐳 Docker

El proyecto incluye:

- Dockerfile
- Docker Compose
- PostgreSQL
- Entrypoint automático
- Healthcheck de PostgreSQL
- Migraciones automáticas
- Creación automática del administrador inicial

Iniciar el proyecto

docker compose up --build

La API queda disponible en:

http://localhost:8000

Swagger UI:

http://localhost:8000/docs

ReDoc:

http://localhost:8000/redoc

PostgreSQL se ejecuta dentro de un contenedor independiente.

La API se conecta internamente al servicio PostgreSQL mediante la red de Docker.

---

🛑 Detener los contenedores

Para detener los servicios:

docker compose down

Para detenerlos y eliminar también los volúmenes:

docker compose down -v

«"docker compose down -v" elimina los datos persistidos del contenedor de PostgreSQL y debe utilizarse principalmente cuando se quiere comenzar con una base de datos limpia.»

---

⚙️ Variables de entorno

La aplicación utiliza variables de entorno para configurar la conexión a la base de datos y la autenticación JWT.

Ejemplo:

DATABASE_URL=postgresql://inventory_user:inventory_password@db:5432/inventory_db
JWT_SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

Para la creación automática del administrador:

ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@inventory.local
ADMIN_PASSWORD=change_this_admin_password

El archivo ".env" contiene valores específicos del entorno y no debe subirse al repositorio.

El proyecto incluye ".env.example" como plantilla.

---

📁 Estructura del proyecto

gestion de inventario-api/
│
├── app/
│   ├── dependencies/
│   │   └── auth.py
│   │
│   ├── models/
│   │   ├── category.py
│   │   ├── product.py
│   │   ├── stock_movement.py
│   │   └── user.py
│   │
│   ├── routes/
│   │   ├── auth.py
│   │   ├── category.py
│   │   ├── product.py
│   │   └── stock_movement.py
│   │
│   ├── schemas/
│   │   ├── category.py
│   │   ├── product.py
│   │   ├── stock_movement.py
│   │   └── user.py
│   │
│   ├── scripts/
│   │   └── create_admin.py
│   │
│   ├── services/
│   │   ├── admin.py
│   │   ├── category.py
│   │   ├── product.py
│   │   ├── stock_movement.py
│   │   └── user.py
│   │
│   ├── config.py
│   ├── database.py
│   ├── logging.py
│   └── main.py
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── docker/
│   └── entrypoint.sh
│
├── tests/
│   ├── test_auth.py
│   ├── test_categories.py
│   ├── test_products.py
│   └── test_stock_movements.py
│
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
└── README.md

---

🧪 Tests

El proyecto cuenta actualmente con:

77 tests

Los tests utilizan:

pytest
SQLite en memoria

Esto permite ejecutar la suite sin depender de una instancia externa de PostgreSQL.

Para ejecutar todos los tests:

pytest -v

Resultado actual:

77 passed

La suite cubre principalmente:

- Registro y usuarios
- Hash de contraseñas
- Autenticación
- JWT
- Tokens expirados
- Autorización
- Roles
- Usuarios inactivos
- Categorías
- Soft delete
- Productos
- Validaciones
- Paginación y filtros
- Movimientos de stock
- Control de stock
- Historial de movimientos

---

🔑 Swagger / OpenAPI

FastAPI genera automáticamente la documentación interactiva.

Swagger UI:

http://localhost:8000/docs

ReDoc:

http://localhost:8000/redoc

El login utiliza OAuth2 Password Flow y permite utilizar el botón Authorize de Swagger para probar endpoints protegidos.

---

🛡️ Seguridad

El proyecto implementa:

- JWT
- Expiración de tokens
- Hash de contraseñas mediante Argon2
- Autenticación basada en OAuth2
- Control de acceso por roles
- Usuarios activos/inactivos
- Variables sensibles mediante ".env"
- Separación entre usuarios normales y administradores

Los secretos y credenciales específicas del entorno no deben almacenarse en el repositorio.

---

📝 Manejo de errores

La API incorpora manejo de errores HTTP y validaciones para evitar operaciones inválidas.

Entre otros casos se controlan:

- Recursos inexistentes
- Usuarios duplicados
- Categorías inexistentes
- Categorías inactivas
- Productos inexistentes
- Productos inactivos
- Stock insuficiente
- Cantidades inválidas
- Tipos de movimiento inválidos
- Usuarios sin permisos
- Tokens inválidos o expirados

---

🪵 Logging

La aplicación incorpora logging para facilitar el seguimiento y diagnóstico de eventos relevantes de la API.

---

🔧 Configuración

La configuración de la aplicación se centraliza en:

app/config.py

Se utilizan variables de entorno para evitar almacenar directamente en el código valores específicos del entorno.

---

🚀 Ejecución local

Crear y activar un entorno virtual:

Windows

python -m venv .venv
.\.venv\Scripts\Activate.ps1

Instalar dependencias:

pip install -r requirements.txt

Configurar las variables de entorno utilizando:

.env.example

y crear el archivo:

.env

Luego iniciar la aplicación:

uvicorn app.main:app --reload

La API estará disponible en:

http://localhost:8000

---

🐳 Ejecución con Docker

Para ejecutar todo el entorno mediante Docker:

docker compose up --build

El flujo de inicio es:

PostgreSQL
    ↓
Healthcheck
    ↓
entrypoint.sh
    ↓
Alembic
    ↓
Creación del administrador inicial
    ↓
FastAPI / Uvicorn

---

📌 Estado del proyecto

El proyecto se encuentra actualmente funcional y preparado como proyecto de portfolio.

Implementado

- [x] FastAPI
- [x] SQLAlchemy
- [x] Pydantic
- [x] PostgreSQL
- [x] SQLite para tests
- [x] Autenticación JWT
- [x] OAuth2 Password Flow
- [x] Hash de contraseñas con Argon2
- [x] Usuarios
- [x] Roles
- [x] Autorización
- [x] Categorías
- [x] Productos
- [x] Soft delete
- [x] Paginación
- [x] Filtros
- [x] Movimientos de stock
- [x] Historial de movimientos
- [x] Manejo de errores
- [x] Logging
- [x] Variables de entorno
- [x] Docker
- [x] Docker Compose
- [x] Alembic
- [x] Administrador inicial automático
- [x] Tests automatizados
- [x] Documentación Swagger/OpenAPI

---

📄 Licencia

Este proyecto fue desarrollado como proyecto de portfolio.