import bcrypt
import jwt
import re
import requests

from datetime import datetime, timedelta

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .enums import HttpStatus, ResponseMessage
from .middleware import rate_limit, require_unauthenticated
from .models import User

from django.views.decorators.http import require_GET


def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_jwt_token(user_id: int) -> str:
    payload = {
        "id": user_id,
        "exp": datetime.utcnow() + timedelta(days=7),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


@csrf_exempt
@require_http_methods(["POST"])
@require_unauthenticated
@rate_limit(requests_per_period=5, period_seconds=180)
def sign_up(request):
    data = request.json_data
    
    first_name = data.get("firstName", "").strip()
    middle_name = data.get("middleName", "").strip() or None
    last_name = data.get("lastName", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    
    errors = {}
    
    if not first_name:
        errors["firstName"] = "First name is required"
    
    if not last_name:
        errors["lastName"] = "Last name is required"
    
    if not email:
        errors["email"] = "Email is required"
    elif not validate_email(email):
        errors["email"] = "Invalid email format"
    
    if not password:
        errors["password"] = "Password is required"
    elif len(password) < 6:
        errors["password"] = "Password must be at least 6 characters"
    
    if errors:
        return JsonResponse(
            {"errors": errors, "message": ResponseMessage.VALIDATION_ERROR},
            status=HttpStatus.UNPROCESSABLE_ENTITY
        )
    
    if User.objects.filter(email=email).exists():
        return JsonResponse(
            {"error": ResponseMessage.EMAIL_ALREADY_EXISTS},
            status=HttpStatus.CONFLICT
        )
    
    password_hash = hash_password(password)
    
    user = User.objects.create(
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        email=email,
        password_hash=password_hash
    )
    
    token = create_jwt_token(user.id)
    
    response = JsonResponse(
        {
            "message": ResponseMessage.USER_CREATED,
            "user": {
                "id": user.id,
                "firstName": user.first_name,
                "middleName": user.middle_name,
                "lastName": user.last_name,
                "email": user.email
            }
        },
        status=HttpStatus.CREATED
    )
    
    response.set_cookie(
        key="auth",
        value=token,
        max_age=7 * 24 * 60 * 60,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax"
    )
    
    return response


@csrf_exempt
@require_http_methods(["POST"])
@require_unauthenticated
def log_in(request):
    data = request.json_data
    
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    
    errors = {}
    
    if not email:
        errors["email"] = "Email is required"
    elif not validate_email(email):
        errors["email"] = "Invalid email format"
    
    if not password:
        errors["password"] = "Password is required"
    
    if errors:
        return JsonResponse(
            {"errors": errors, "message": ResponseMessage.VALIDATION_ERROR},
            status=HttpStatus.UNPROCESSABLE_ENTITY
        )
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse(
            {"error": ResponseMessage.INVALID_CREDENTIALS},
            status=HttpStatus.UNAUTHORIZED
        )
    
    if not verify_password(password, user.password_hash):
        return JsonResponse(
            {"error": ResponseMessage.INVALID_CREDENTIALS},
            status=HttpStatus.UNAUTHORIZED
        )
    
    token = create_jwt_token(user.id)
    
    response = JsonResponse(
        {
            "message": ResponseMessage.USER_LOGGED_IN,
            "user": {
                "id": user.id,
                "firstName": user.first_name,
                "middleName": user.middle_name,
                "lastName": user.last_name,
                "email": user.email
            }
        },
        status=HttpStatus.OK
    )
    
    response.set_cookie(
        key="auth",
        value=token,
        max_age=7 * 24 * 60 * 60,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax"
    )
    
    return response


@csrf_exempt
@require_http_methods(["POST"])
def log_out(request):
    if request.user is None:
        return JsonResponse(
            {"error": ResponseMessage.UNAUTHORIZED},
            status=HttpStatus.UNAUTHORIZED
        )
    
    response = JsonResponse(
        {"message": ResponseMessage.USER_LOGGED_OUT},
        status=HttpStatus.OK
    )
    
    response.delete_cookie("auth")
    
    return response

@csrf_exempt
@require_GET
def github_avatar(request):
    """
    Отримує аватар користувача через публічний GitHub API.
    GET /api/auth/github-avatar/?email=user@example.com
    """
    email = request.GET.get("email", "").strip()
    if not email:
        return JsonResponse(
            {"error": "Email is required"},
            status=HttpStatus.BAD_REQUEST
        )

    try:
        # Крок 1: шукаємо користувача GitHub за email
        search_url = f"https://api.github.com/search/users?q={email}+in:email"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "TodoManager/1.0"
        }
        resp = requests.get(search_url, headers=headers, timeout=5)

        if resp.status_code != 200:
            return JsonResponse(
                {"avatarUrl": None, "username": None, "source": "github"}
            )

        data = resp.json()
        if not data.get("items"):
            return JsonResponse(
                {"avatarUrl": None, "username": None, "source": "github"}
            )

        username = data["items"][0]["login"]
        avatar_url = data["items"][0]["avatar_url"]

        return JsonResponse({
            "avatarUrl": avatar_url,
            "username": username,
            "source": "github"
        })

    except Exception as e:
        return JsonResponse(
            {"error": str(e), "avatarUrl": None},
            status=HttpStatus.INTERNAL_SERVER_ERROR
        )

@csrf_exempt
@require_GET
def get_me(request):
    """
    Повертає дані поточного авторизованого користувача.
    """
    token = request.COOKIES.get("auth")
    if not token:
        return JsonResponse({"error": ResponseMessage.UNAUTHORIZED}, status=HttpStatus.UNAUTHORIZED)
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user = User.objects.get(id=payload.get("id"))
        
        return JsonResponse({
            "email": user.email,
            "firstName": user.first_name,
            "lastName": user.last_name
        })
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return JsonResponse({"error": ResponseMessage.UNAUTHORIZED}, status=HttpStatus.UNAUTHORIZED)