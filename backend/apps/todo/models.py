from django.db import models

from apps.accounts.models import User


class TodoList(models.Model):
    id = models.AutoField(
        primary_key=True,
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="user_id",
        related_name="todo_lists",
    )

    title = models.CharField(
        max_length=255,
        null=False,
        blank=False,
    )

    description = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "todo_lists"

    def __str__(self):
        return self.title


class TodoItem(models.Model):
    id = models.AutoField(
        primary_key=True,
    )

    todo_list = models.ForeignKey(
        TodoList,
        on_delete=models.CASCADE,
        db_column="list_id",
        related_name="todo_items",
    )

    title = models.CharField(
        max_length=500,
        null=False,
        blank=False,
    )

    description = models.CharField(
        max_length=4096,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "todo_items"

    def __str__(self):
        return self.title