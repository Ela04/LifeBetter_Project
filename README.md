# 🏢 LifeBetter - Sistema de Gestión de Condominios y Gastos Comunes

Plataforma web modular para la administración transparente de condominios, emisión e integración de pagos de gastos comunes mediante **Transbank Webpay Plus** y reserva de espacios comunes.

---

## 🛠️ Stack Técnico

* **Backend:** Python 3.12+ | Django 5+ | Django REST Framework
* **Pasarela de Pagos:** Transbank Webpay Plus SDK (v4+)
* **Frontend:** HTML5 | CSS3 | Bootstrap 5.3 | Bootstrap Icons
* **Base de Datos:** PostgreSQL / SQLite3
* **Arquitectura:** Domain-Driven Design (Modular) | RBAC | Clean Code

---

## 🚀 Instalación y Puesta en Marcha Local

### 1. Clonar el repositorio

git clone [https://github.com/Ela04/LifeBetterDjango.git](https://github.com/Ela04/LifeBetterDjango.git)
cd LifeBetterDjango

### 2. Crear y activar el entorno virtual en PowerShell

python -m venv env
.\env\Scripts\activate

### 3. Instalar dependencias en PowerShell

pip install --upgrade pip
pip install -r requirements.txt

### 4. Configurar variables de entorno

Copia la plantilla .env.example y crea un archivo .env en la raíz con tus credenciales:

Copy-Item .env.example .env

### 5. Ejecutar migraciones e inicializar base de datos en PowerShell

python src/manage.py migrate
python src/manage.py seed_data

### 6. Iniciar servidor de desarrollo en PowerShell

python src/manage.py runserver