from django.http import HttpResponse
from django.views.decorators.http import require_GET


@require_GET
def about_view(request):
    html = """
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <title>Про проєкт — Todo Manager</title>
        <style>
            body { font-family: -apple-system, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 20px; color: #333; line-height: 1.6; }
            h1 { color: #667eea; }
            a { color: #667eea; }
            .back { display: inline-block; margin-top: 20px; padding: 8px 16px; background: #667eea; color: white; text-decoration: none; border-radius: 6px; }
        </style>
    </head>
    <body>
        <h1>📝 Todo Manager</h1>
        <p>Навчальний проєкт з дисципліни "Розробка веб-інтерфейсів та middleware".</p>
        <h2>Стек технологій</h2>
        <ul>
            <li><b>Backend:</b> Python 3.11, Django 5.x, Django REST Framework, MySQL 8</li>
            <li><b>Frontend:</b> React 18, Vite, React Router, Axios</li>
            <li><b>Auth:</b> JWT токени в HTTP-only cookies, bcrypt хешування паролів</li>
        </ul>
        <h2>Можливості</h2>
        <ul>
            <li>Реєстрація та авторизація користувачів</li>
            <li>CRUD для списків завдань та самих завдань</li>
            <li>Розмежування прав: звичайні користувачі vs адміністратори</li>
            <li>Rate limiting для захисту від зловживань</li>
        </ul>
        <a class="back" href="/">← Повернутися до застосунку</a>
    </body>
    </html>
    """
    return HttpResponse(html)


@require_GET
def help_view(request):
    html = """
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <title>Допомога — Todo Manager</title>
        <style>
            body { font-family: -apple-system, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 20px; color: #333; line-height: 1.6; }
            h1 { color: #667eea; }
            a { color: #667eea; }
            code { background: #f4f4f4; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }
            .back { display: inline-block; margin-top: 20px; padding: 8px 16px; background: #667eea; color: white; text-decoration: none; border-radius: 6px; }
        </style>
    </head>
    <body>
        <h1>❓ Допомога</h1>
        <h2>Як почати?</h2>
        <ol>
            <li>Зареєструйтесь на сторінці <code>/sign-up</code></li>
            <li>Увійдіть у свій акаунт</li>
            <li>Створіть перший список завдань</li>
            <li>Додавайте завдання всередину списку</li>
        </ol>
        <h2>Гарячі клавіші</h2>
        <ul>
            <li><b>Enter</b> — зберегти редагування</li>
            <li><b>Escape</b> — скасувати редагування</li>
            <li><b>Shift+Enter</b> — новий рядок у описі</li>
        </ul>
        <h2>API документація</h2>
        <p>Swagger UI доступний за адресою <a href="/api/docs/">/api/docs/</a></p>
        <a class="back" href="/">← Повернутися до застосунку</a>
    </body>
    </html>
    """
    return HttpResponse(html)