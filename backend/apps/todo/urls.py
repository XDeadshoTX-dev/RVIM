from django.urls import path

from . import views

urlpatterns = [
    path("lists", views.get_user_todo_lists, name="get_todo_lists"),
    path("lists/create", views.create_todo_list, name="create_todo_list"),
    path("lists/<int:list_id>", views.update_todo_list, name="update_todo_list"),
    path("lists/<int:list_id>/delete", views.delete_todo_list, name="delete_todo_list"),
    path("lists/<int:list_id>/items", views.get_todo_list_items, name="get_todo_items"),
    
    path("items/create", views.create_todo_item, name="create_todo_item"),
    path("items/<int:item_id>", views.update_todo_item, name="update_todo_item"),
    path("items/<int:item_id>/delete", views.delete_todo_item, name="delete_todo_item"),
]