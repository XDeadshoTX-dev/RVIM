# Звіт з продуктивності — Todo Manager (ЛР4)

## 1. Опис застосунку
Todo Manager — веб-застосунок для управління списками завдань.
Стек: Python 3.11 + Django 5.x + MySQL 8 + React 18 + Vite.

## 2. Середовища тестування

| Середовище | Конфігурація |
|------------|--------------|
| localhost | Windows 11, Intel i7, 16GB RAM, Python 3.11 |
| Docker | mysql:8.0 + gunicorn (3 workers) + nginx |
| Cloud (опціонально) | 1 vCPU, 512MB RAM, Linux |

## 3. Сценарії навантаження (Locust)

| Сценарій | Вага | Опис |
|----------|:----:|------|
| GET /api/todo/lists | 5 | Читання списків |
| POST /api/todo/lists/create | 2 | Створення списку |
| POST /api/todo/items/create | 1 | Створення завдання |
| GET /about/ | 1 | Статична сторінка |

## 4. Результати

### Тест 1: 10 користувачів, 60 секунд
| Метрика | localhost | Docker |
|---------|-----------|--------|
| RPS | | |
| Середній час (мс) | | |
| p95 (мс) | | |
| p99 (мс) | | |
| % помилок | | |

### Тест 2: 50 користувачів, 60 секунд
| Метрика | localhost | Docker |
|---------|-----------|--------|
| RPS | | |
| Середній час (мс) | | |
| p95 (мс) | | |
| p99 (мс) | | |
| % помилок | | |

## 5. Графіки
(скріншоти з Locust UI: Statistics, Response Times, Users)

## 6. Висновки
- Застосунок витримує до ___ одночасних користувачів
- Основне вузьке місце: ___
- Рекомендації: індекси БД, кешування, connection pooling

## 7. Команди для відтворення
```bash
# Backend
cd backend && python manage.py runserver

# Locust
pip install locust
locust -f tests/locustfile.py --host=http://localhost:8000
# Відкрийте http://localhost:8089

# Docker
docker compose up --build