# 📄 Сервис обработки загружаемых документов

## Описание проекта

Веб-сервис для загрузки, хранения и обработки технической документации. 
Позволяет зарегистрированным пользователям загружать документы (DWG, PDF, DOCX, Excel, JPG 
до 100 МБ). Администратор рассматривает документы и отправляет уведомления пользователям.

## 🏗️ Архитектура проекта

- **Backend**: Django + Django Rest Framework
- **База данных**: PostgreSQL
- **Очередь задач**: Celery + Redis
- **Контейнеризация**: Docker + Docker Compose
- **Документация API**: Swagger (drf-spectacular)

## 🚀 Быстрый старт

### Требования
- Docker и Docker Compose
- Git

### Установка и запуск

# Клонирование репозитория
git clone https://github.com/Ekaterina-RA/Graduation_project.git
cd Graduation_project

# Создание .env файла
cp .env.example .env

# Запуск всех сервисов
docker-compose up -d --build

# Применение миграций
docker-compose exec web python manage.py migrate

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# Сервис доступен по адресу:
# API: http://localhost:8000/api/v1/
# Swagger: http://localhost:8000/api/docs/
# Admin: http://localhost:8000/admin/
\`\`\`

## 📁 Структура проекта


Graduation_project/
├── config/              # Настройки проекта
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
├── documents/           # Приложение документов
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── admin.py
│   ├── tasks.py
│   ├── urls.py
│   └── tests/
├── users/               # Приложение пользователей
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   └── tests/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── pytest.ini
└── README.md


## 📡 API Endpoints

| Метод | URL | Описание |
|-------|-----|----------|
| POST | /api/v1/users/register/ | Регистрация |
| POST | /api/v1/users/login/ | Авторизация |
| GET | /api/v1/users/profile/ | Профиль |
| GET | /api/v1/documents/ | Список документов |
| POST | /api/v1/documents/ | Загрузить документ |
| GET | /api/v1/documents/{id}/ | Детали документа |
| POST | /api/v1/documents/{id}/review/ | Рассмотреть (админ) |

## 🧪 Тестирование


docker-compose exec web pytest --cov=. --cov-report=term-missing


## 🏷️ Теги проекта
CORS, DRF, Django, Git, ORM, OpenAPIDocs, PEP8, PostgreSQL, README, Tests, Docker, Docker-Compose