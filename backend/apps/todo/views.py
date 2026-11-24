import json
from functools import wraps

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.accounts.enums import HttpStatus, ResponseMessage
from apps.accounts.middleware import rate_limit, get_client_ip
from apps.accounts.models import AdminUser
from .models import TodoList, TodoItem


def require_authenticated_non_admin(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.user is None:
            return JsonResponse(
                {"error": ResponseMessage.UNAUTHORIZED},
                status=HttpStatus.UNAUTHORIZED
            )
        
        try:
            AdminUser.objects.get(user_id=request.user.id)
            return JsonResponse(
                {"error": "API not available for administrators"},
                status=HttpStatus.FORBIDDEN
            )
        except AdminUser.DoesNotExist:
            pass
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


def validate_todo_list_data(data, partial=False):
    errors = {}
    
    title = data.get("title")
    description = data.get("description")
    
    if not partial or title is not None:
        if not title or not str(title).strip():
            errors["title"] = "Title is required"
        elif len(str(title).strip()) > 255:
            errors["title"] = "Title must be less than 255 characters"
    
    if description is not None and len(str(description)) > 1024:
        errors["description"] = "Description must be less than 1024 characters"
    
    return errors


def validate_todo_item_data(data, partial=False):
    errors = {}
    
    title = data.get("title")
    description = data.get("description")
    list_id = data.get("listId")
    
    if not partial or title is not None:
        if not title or not str(title).strip():
            errors["title"] = "Title is required"
        elif len(str(title).strip()) > 500:
            errors["title"] = "Title must be less than 500 characters"
    
    if description is not None and len(str(description)) > 4096:
        errors["description"] = "Description must be less than 4096 characters"
    
    if not partial and list_id is None:
        errors["listId"] = "List ID is required"
    elif list_id is not None:
        try:
            int(list_id)
        except (ValueError, TypeError):
            errors["listId"] = "List ID must be an integer"
    
    return errors


def format_todo_list(todo_list):
    return {
        "id": todo_list.id,
        "title": todo_list.title,
        "description": todo_list.description,
        "createdAt": todo_list.created_at.isoformat() if todo_list.created_at else None,
        "updatedAt": todo_list.updated_at.isoformat() if todo_list.updated_at else None,
    }


def format_todo_item(todo_item):
    return {
        "id": todo_item.id,
        "listId": todo_item.todo_list_id,
        "title": todo_item.title,
        "description": todo_item.description,
        "createdAt": todo_item.created_at.isoformat() if todo_item.created_at else None,
        "updatedAt": todo_item.updated_at.isoformat() if todo_item.updated_at else None,
    }


@csrf_exempt
@require_http_methods(["POST"])
@require_authenticated_non_admin
@rate_limit(requests_per_period=30, period_seconds=60)
def create_todo_list(request):
    data = request.json_data
    
    errors = validate_todo_list_data(data)
    
    if errors:
        return JsonResponse(
            {"errors": errors, "message": ResponseMessage.VALIDATION_ERROR},
            status=HttpStatus.UNPROCESSABLE_ENTITY
        )
    
    todo_list = TodoList.objects.create(
        user=request.user,
        title=str(data["title"]).strip(),
        description=data.get("description")
    )
    
    return JsonResponse(
        {
            "message": "Todo list created successfully",
            "data": format_todo_list(todo_list)
        },
        status=HttpStatus.CREATED
    )


@csrf_exempt
@require_http_methods(["PATCH"])
@require_authenticated_non_admin
@rate_limit(requests_per_period=60, period_seconds=60)
def update_todo_list(request, list_id):
    try:
        todo_list = TodoList.objects.get(id=list_id)
    except TodoList.DoesNotExist:
        return JsonResponse(
            {"error": "Todo list not found"},
            status=HttpStatus.NOT_FOUND
        )
    
    if todo_list.user_id != request.user.id:
        return JsonResponse(
            {"error": ResponseMessage.FORBIDDEN},
            status=HttpStatus.FORBIDDEN
        )
    
    data = request.json_data
    
    errors = validate_todo_list_data(data, partial=True)
    
    if errors:
        return JsonResponse(
            {"errors": errors, "message": ResponseMessage.VALIDATION_ERROR},
            status=HttpStatus.UNPROCESSABLE_ENTITY
        )
    
    if "title" in data:
        todo_list.title = str(data["title"]).strip()
    
    if "description" in data:
        todo_list.description = data.get("description")
    
    todo_list.save()
    
    return JsonResponse(
        {
            "message": "Todo list updated successfully",
            "data": format_todo_list(todo_list)
        },
        status=HttpStatus.OK
    )


@csrf_exempt
@require_http_methods(["DELETE"])
@require_authenticated_non_admin
@rate_limit(requests_per_period=60, period_seconds=60)
def delete_todo_list(request, list_id):
    try:
        todo_list = TodoList.objects.get(id=list_id)
    except TodoList.DoesNotExist:
        return JsonResponse(
            {"error": "Todo list not found"},
            status=HttpStatus.NOT_FOUND
        )
    
    if todo_list.user_id != request.user.id:
        return JsonResponse(
            {"error": ResponseMessage.FORBIDDEN},
            status=HttpStatus.FORBIDDEN
        )
    
    todo_list.delete()
    
    return JsonResponse(
        {"message": "Todo list deleted successfully"},
        status=HttpStatus.OK
    )


@csrf_exempt
@require_http_methods(["POST"])
@require_authenticated_non_admin
@rate_limit(requests_per_period=30, period_seconds=60)
def create_todo_item(request):
    data = request.json_data
    
    errors = validate_todo_item_data(data)
    
    if errors:
        return JsonResponse(
            {"errors": errors, "message": ResponseMessage.VALIDATION_ERROR},
            status=HttpStatus.UNPROCESSABLE_ENTITY
        )
    
    try:
        todo_list = TodoList.objects.get(id=data["listId"])
    except TodoList.DoesNotExist:
        return JsonResponse(
            {"error": "Todo list not found"},
            status=HttpStatus.NOT_FOUND
        )
    
    if todo_list.user_id != request.user.id:
        return JsonResponse(
            {"error": ResponseMessage.FORBIDDEN},
            status=HttpStatus.FORBIDDEN
        )
    
    todo_item = TodoItem.objects.create(
        todo_list=todo_list,
        title=str(data["title"]).strip(),
        description=data.get("description")
    )
    
    return JsonResponse(
        {
            "message": "Todo item created successfully",
            "data": format_todo_item(todo_item)
        },
        status=HttpStatus.CREATED
    )


@csrf_exempt
@require_http_methods(["PATCH"])
@require_authenticated_non_admin
@rate_limit(requests_per_period=60, period_seconds=60)
def update_todo_item(request, item_id):
    try:
        todo_item = TodoItem.objects.get(id=item_id)
    except TodoItem.DoesNotExist:
        return JsonResponse(
            {"error": "Todo item not found"},
            status=HttpStatus.NOT_FOUND
        )
    
    if todo_item.todo_list.user_id != request.user.id:
        return JsonResponse(
            {"error": ResponseMessage.FORBIDDEN},
            status=HttpStatus.FORBIDDEN
        )
    
    data = request.json_data
    
    errors = validate_todo_item_data(data, partial=True)
    
    if errors:
        return JsonResponse(
            {"errors": errors, "message": ResponseMessage.VALIDATION_ERROR},
            status=HttpStatus.UNPROCESSABLE_ENTITY
        )
    
    if "title" in data:
        todo_item.title = str(data["title"]).strip()
    
    if "description" in data:
        todo_item.description = data.get("description")
    
    if "listId" in data:
        try:
            new_list = TodoList.objects.get(id=data["listId"])
            if new_list.user_id != request.user.id:
                return JsonResponse(
                    {"error": ResponseMessage.FORBIDDEN},
                    status=HttpStatus.FORBIDDEN
                )
            todo_item.todo_list = new_list
        except TodoList.DoesNotExist:
            return JsonResponse(
                {"error": "Todo list not found"},
                status=HttpStatus.NOT_FOUND
            )
    
    todo_item.save()
    
    return JsonResponse(
        {
            "message": "Todo item updated successfully",
            "data": format_todo_item(todo_item)
        },
        status=HttpStatus.OK
    )


@csrf_exempt
@require_http_methods(["DELETE"])
@require_authenticated_non_admin
@rate_limit(requests_per_period=60, period_seconds=60)
def delete_todo_item(request, item_id):
    try:
        todo_item = TodoItem.objects.get(id=item_id)
    except TodoItem.DoesNotExist:
        return JsonResponse(
            {"error": "Todo item not found"},
            status=HttpStatus.NOT_FOUND
        )
    
    if todo_item.todo_list.user_id != request.user.id:
        return JsonResponse(
            {"error": ResponseMessage.FORBIDDEN},
            status=HttpStatus.FORBIDDEN
        )
    
    todo_item.delete()
    
    return JsonResponse(
        {"message": "Todo item deleted successfully"},
        status=HttpStatus.OK
    )


@csrf_exempt
@require_http_methods(["GET"])
@require_authenticated_non_admin
def get_user_todo_lists(request):
    todo_lists = TodoList.objects.filter(user=request.user).order_by("-created_at")
    
    return JsonResponse(
        {
            "data": [format_todo_list(tl) for tl in todo_lists]
        },
        status=HttpStatus.OK
    )


@csrf_exempt
@require_http_methods(["GET"])
@require_authenticated_non_admin
def get_todo_list_items(request, list_id):
    try:
        todo_list = TodoList.objects.get(id=list_id)
    except TodoList.DoesNotExist:
        return JsonResponse(
            {"error": "Todo list not found"},
            status=HttpStatus.NOT_FOUND
        )
    
    if todo_list.user_id != request.user.id:
        return JsonResponse(
            {"error": ResponseMessage.FORBIDDEN},
            status=HttpStatus.FORBIDDEN
        )
    
    todo_items = TodoItem.objects.filter(todo_list=todo_list).order_by("-created_at")
    
    return JsonResponse(
        {
            "data": [format_todo_item(ti) for ti in todo_items]
        },
        status=HttpStatus.OK
    )