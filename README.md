# Django E-commerce

Tienda online completa desarrollada con Django 5.x y Bootstrap 5.

## Requisitos

- Python 3.11+
- PostgreSQL (opcional, por defecto SQLite)

## Configuración e Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone <ruta_al_repo>
    cd ecommerce
    ```

2.  **Crear entorno virtual:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install django pillow psycopg2-binary
    ```

4.  **Configurar base de datos:**
    Por defecto usa SQLite. Para PostgreSQL, configurar variables de entorno en `.env` (no incluido por defecto).
    
    Ver `ecommerce/settings.py` para detalles.

5.  **Migraciones:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6.  **Crear superusuario:**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Ejecutar servidor:**
    ```bash
    python manage.py runserver
    ```
# Tienda-E-Commerce-Google-Antigravity
