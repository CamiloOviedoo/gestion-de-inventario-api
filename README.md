Inventory Management API

REST API para la gestión de inventario desarrollada con Python y FastAPI, con autenticación mediante JWT, autorización por roles, PostgreSQL, SQLAlchemy, migraciones con Alembic y ejecución mediante Docker.

El proyecto está orientado a simular una API backend real para administrar usuarios, categorías, productos y movimientos de stock.

---

🚀 Tecnologías

- Python 3.13
- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL
- JWT / OAuth2
- Alembic
- Pytest
- SQLite para pruebas
- Docker
- Docker Compose

---

📋 Funcionalidades

🔐 Autenticación y autorización

- Registro de usuarios.
- Login mediante OAuth2 Password Flow.
- Autenticación mediante tokens JWT.
- Hash seguro de contraseñas.
- Validación de tokens.
- Control de expiración de tokens.
- Endpoint "/auth/me".
- Usuarios activos e inactivos.
- Sistema de roles:
  - "user"
  - "admin"
- Protección de endpoints según permisos.

📦 Categorías

- Crear categorías.
- Consultar categorías.
- Actualizar categorías.
- Eliminación lógica (soft delete).
- Las categorías desactivadas no aparecen en los listados.
- Acceso restringido para operaciones administrativas.

🛒 Productos

- Crear productos.
- Consultar productos.
- Actualizar productos.
- Eliminación lógica.
- Validación de precios y stock.
- Validación de categoría existente y activa.
- Filtros de búsqueda.
- Paginación.
- Control de acceso según rol.

📊 Movimientos de stock

- Registro de entradas y salidas.
- Tipos de movimiento mediante "MovementType".
- Las entradas incrementan el stock.
- Las salidas disminuyen el stock.
- Validación de cantidades.
- Prevención de stock insuficiente.
- Historial de movimientos por producto.
- Acceso administrativo para registrar movimientos.

🗄️ Base de datos

- PostgreSQL como base de datos principal.
- SQLAlchemy como ORM.
- Relaciones entre entidades.
- Migraciones administradas mediante Alembic.
- SQLite en memoria para las pruebas automatizadas.

🐳 Docker

El proyecto está preparado para ejecutarse mediante:

- Docker
- Docker Compose
- API FastAPI
- PostgreSQL

La aplicación y la base de datos se ejecutan como servicios independientes.

🧪 Testing

El proyecto cuenta con una suite de pruebas automatizadas utilizando Pytest.

Estado actual de la suite:

77 passed

Las pruebas cubren los principales componentes de la aplicación, incluyendo autenticación, autorización, CRUD, validaciones, categorías, productos y movimientos de stock.

---

🏗️ Arquitectura del proyecto

La aplicación utiliza una estructura modular separando responsabilidades entre rutas, modelos, esquemas, servicios y dependencias.

'''text
gestion-de-inventario-api/
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
│   ├── services/
│   │   └── ...
│   │
│   ├── config.py
│   ├── database.py
│   └── main.py
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── tests/
│   └── ...
│
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
├── alembic.ini
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
'''
---

🔑 Seguridad

La API utiliza autenticación basada en JWT.

Las contraseñas no se almacenan directamente, sino que se almacenan utilizando hashing seguro.

Los endpoints protegidos requieren autenticación y determinadas operaciones administrativas requieren el rol "admin".

El token se obtiene mediante el endpoint de login y posteriormente puede utilizarse desde Swagger mediante el botón Authorize.

---

⚙️ Configuración

La aplicación utiliza variables de entorno para la configuración.

Crear un archivo ".env" a partir de ".env.example":

DATABASE_URL=postgresql+psycopg://inventory_user:inventory_password@db:5432/inventory_db

JWT_SECRET_KEY=your-secret-key

JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30

«No se debe subir el archivo ".env" al repositorio.»

---

🐳 Ejecución con Docker

1. Clonar el repositorio

git clone <URL_DEL_REPOSITORIO>
cd gestion-de-inventario-api

2. Configurar las variables de entorno

Crear el archivo ".env" utilizando ".env.example" como referencia.

3. Construir y ejecutar los servicios

docker compose up --build

La API estará disponible en:

http://localhost:8000

4. Swagger

La documentación interactiva estará disponible en:

http://localhost:8000/docs

También está disponible la documentación alternativa de OpenAPI:

http://localhost:8000/redoc

5. Detener los servicios

docker compose down

Para detener los servicios y eliminar también los volúmenes:

docker compose down -v

«"-v" elimina los datos persistidos de PostgreSQL, por lo que debe utilizarse con precaución.»

---

🗃️ Migraciones con Alembic

Las modificaciones del esquema de la base de datos se administran mediante Alembic.

Para ejecutar las migraciones:

alembic upgrade head

Para comprobar la versión actual:

alembic current

Para crear una nueva migración después de modificar los modelos:

alembic revision --autogenerate -m "descripcion del cambio"

---

🧪 Ejecutar las pruebas

Instalar las dependencias:

pip install -r requirements.txt

Ejecutar la suite:

pytest -v

Resultado actual:

77 passed

Las pruebas utilizan una base SQLite en memoria para evitar depender de una instancia externa de PostgreSQL durante la ejecución de la suite.

---

📚 Documentación de la API

FastAPI genera automáticamente documentación OpenAPI.

Swagger UI

http://localhost:8000/docs

ReDoc

http://localhost:8000/redoc

Desde Swagger es posible autenticarse mediante Authorize y probar los endpoints protegidos.

---

🧩 Principales endpoints

Authentication

POST /auth/register
POST /auth/login
GET  /auth/me

Categories

GET    /categories
GET    /categories/{category_id}
POST   /categories
PUT    /categories/{category_id}
DELETE /categories/{category_id}

Products

GET    /products
GET    /products/{product_id}
POST   /products
PUT    /products/{product_id}
DELETE /products/{product_id}

Stock movements

POST /stock-movement
GET  /stock-movement
GET  /stock-movement/{movement_id}

«Las operaciones protegidas requieren autenticación y, dependiendo del endpoint, permisos de administrador.»

---

🔄 Gestión de stock

Los movimientos de inventario utilizan dos tipos principales:

ENTRADA
SALIDA

Una entrada incrementa el stock disponible:

stock actual + cantidad

Una salida disminuye el stock:

stock actual - cantidad

La API valida que la cantidad sea válida y que exista stock suficiente antes de realizar una salida.

Además, cada movimiento queda registrado para conservar el historial de operaciones.

---

🧠 Validaciones y manejo de errores

La API incorpora validaciones para evitar datos inconsistentes, incluyendo:

- Precios negativos.
- Stock negativo.
- Cantidades de movimientos inválidas.
- Salidas superiores al stock disponible.
- Categorías inexistentes.
- Categorías inactivas.
- Usuarios duplicados.
- Emails duplicados.
- Usuarios inactivos.
- Tokens inválidos o expirados.
- Acceso a recursos eliminados lógicamente.
- Operaciones sin los permisos necesarios.

Los errores se gestionan mediante respuestas HTTP apropiadas y mensajes descriptivos.

---

📝 Soft Delete

Las categorías y productos utilizan eliminación lógica.

En lugar de eliminar físicamente el registro de la base de datos, se modifica su estado mediante un campo de activación.

Esto permite:

- conservar la información histórica;
- evitar perder relaciones existentes;
- ocultar recursos eliminados de los listados;
- mantener consistencia en el historial.

---

📄 Licencia

Este proyecto fue desarrollado como proyecto de portfolio para demostrar conocimientos de desarrollo backend con Python, FastAPI, bases de datos relacionales, autenticación, testing, Docker y migraciones.

---

👨‍💻 Proyecto

Inventory Management API

Backend REST desarrollado con:

Python · FastAPI · PostgreSQL · SQLAlchemy · JWT · Alembic · Pytest · Docker

El proyecto demuestra la implementación de una API backend modular con autenticación, autorización, persistencia de datos, validaciones, gestión de inventario, testing automatizado y entorno reproducible mediante Docker.