@echo off
echo ==========================================
echo Configurando Tienda E-commerce Django
echo ==========================================

REM Verificar si existe venv
if not exist "venv\" (
    echo Creando entorno virtual...
    python -m venv venv
)

echo Activando entorno virtual...
call venv\Scripts\activate

echo Instalando dependencias...
pip install django pillow psycopg2-binary

echo Aplicando migraciones...
python manage.py makemigrations accounts catalog orders cart
python manage.py migrate

echo ==========================================
echo Todo listo. Creando superusuario (opcional)...
echo ==========================================
echo Para crear superusuario ejecuta: python manage.py createsuperuser

echo.
echo Iniciando servidor...
python manage.py runserver
pause
