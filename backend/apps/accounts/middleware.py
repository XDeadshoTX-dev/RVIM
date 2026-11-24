import json
import time
from functools import wraps
from typing import Callable

import jwt
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse

from .enums import HttpStatus, ResponseMessage
from .models import User


class JsonParserMiddleware:
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request):
        if request.content_type and "application/json" in request.content_type:
            try:
                if request.body:
                    request.json_data = json.loads(request.body.decode("utf-8"))
                else:
                    request.json_data = {}
            except json.JSONDecodeError:
                return JsonResponse(
                    {"error": ResponseMessage.INVALID_REQUEST},
                    status=HttpStatus.BAD_REQUEST
                )
        else:
            request.json_data = {}

        response = self.get_response(request)
        return response


class AuthMiddleware:
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request):
        token = request.COOKIES.get("auth")
        user = None

        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = payload.get("id")
                
                if user_id:
                    try:
                        user = User.objects.get(id=user_id)
                    except User.DoesNotExist:
                        user = None
                        
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                user = None

        request.user = user
        response = self.get_response(request)
        return response


def rate_limit(requests_per_period: int, period_seconds: int):
    """
    Rate limiter decorator з використанням timestamp-based підходу.
    Замість cache.expire() використовує збереження timestamp останнього запиту.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            ip = get_client_ip(request)
            cache_key = f"rate_limit:{request.path}:{ip}"
            
            # Отримуємо дані про запити
            request_data = cache.get(cache_key)
            
            if request_data is None:
                # Перший запит - ініціалізуємо
                request_data = {
                    "count": 0,
                    "window_start": time.time()
                }
            
            current_time = time.time()
            window_start = request_data["window_start"]
            elapsed_time = current_time - window_start
            
            # Якщо вікно минуло, скидаємо лічильник
            if elapsed_time >= period_seconds:
                request_data = {
                    "count": 0,
                    "window_start": current_time
                }
            
            # Збільшуємо лічильник
            request_data["count"] += 1
            
            # Зберігаємо оновлені дані з новим таймаутом
            cache.set(cache_key, request_data, period_seconds)
            
            # Виконуємо view
            response = view_func(request, *args, **kwargs)
            
            # Перевіряємо rate limit тільки для успішних відповідей
            if response.status_code < 400:
                if request_data["count"] > requests_per_period:
                    return JsonResponse(
                        {
                            "error": ResponseMessage.RATE_LIMIT_EXCEEDED,
                            "message": f"Rate limit exceeded. Try again in {int(period_seconds - elapsed_time)} seconds"
                        },
                        status=HttpStatus.TOO_MANY_REQUESTS
                    )
            
            return response
        
        return wrapped_view
    return decorator


def require_unauthenticated(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.user is not None:
            return JsonResponse(
                {"error": "User already authenticated"},
                status=HttpStatus.BAD_REQUEST
            )
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")