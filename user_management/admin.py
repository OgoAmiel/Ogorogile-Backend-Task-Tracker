from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "employee_number",
        "department",
        "manager",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "role",
        "department",
        "is_staff",
        "is_active",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Company Info",
            {
                "fields": (
                    "role",
                    "employee_number",
                    "department",
                    "manager",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Company Info",
            {
                "fields": (
                    "role",
                    "employee_number",
                    "department",
                    "manager",
                )
            },
        ),
    )

    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "employee_number",
    )