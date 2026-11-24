from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True)

    first_name = models.CharField(max_length=64, null=False, blank=False)
    middle_name = models.CharField(max_length=64, null=True, blank=True, default=None)
    last_name = models.CharField(max_length=64, null=False, blank=False)
    email = models.CharField(max_length=254, null=False, blank=False, unique=True)
    password_hash = models.CharField(max_length=60, null=False, blank=False)
    
    # Поля для сумісності з Django REST Framework та адмін-панеллю
    is_active = models.BooleanField(default=True, help_text="Чи активний користувач")
    is_staff = models.BooleanField(default=False, help_text="Чи має доступ до адмін-панелі")
    is_superuser = models.BooleanField(default=False, help_text="Чи є суперкористувачем")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email

    # ========================================================
    # ДОДАНО: Методи та властивості для сумісності з Django Auth/Admin
    # ========================================================
    @property
    def is_authenticated(self):
        """Завжди True для реальної моделі користувача"""
        return True

    @property
    def is_anonymous(self):
        """Завжди False для реальної моделі користувача"""
        return False

    def get_username(self):
        """Повертає унікальний ідентифікатор (у нашому випадку це email)"""
        return self.email

    def has_perm(self, perm, obj=None):
        """Перевірка наявності конкретного дозволу"""
        return self.is_superuser

    def has_module_perms(self, app_label):
        """Перевірка наявності дозволів на перегляд додатку"""
        return self.is_superuser
    # ========================================================


class AdminUser(models.Model):
    id = models.AutoField(primary_key=True)

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        db_column="user_id",
        related_name="admin_profile",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "admin_users"

    def __str__(self):
        return f"Admin: {self.user.email}"