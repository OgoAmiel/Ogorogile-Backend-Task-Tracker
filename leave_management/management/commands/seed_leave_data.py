from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from leave_management.models import LeaveType, LeaveBalance

class Command(BaseCommand):
    help = "Seed leave types and create leave balances for existing users"

    def handle(self, *args, **options):
        User = get_user_model()

        leave_type_defaults = [
            {
                "name": "Annual Leave",
                "default_days": 15,
                "requires_attachment": False,
                "is_active": True,
            },
            {
                "name": "Sick Leave",
                "default_days": 10,
                "requires_attachment": False,
                "is_active": True,
            },
            {
                "name": "Family Responsibility Leave",
                "default_days": 3,
                "requires_attachment": False,
                "is_active": True,
            },
            {
                "name": "Unpaid Leave",
                "default_days": 0,
                "requires_attachment": False,
                "is_active": True,
            },
        ]

        created_leave_types = []
        for leave_type_data in leave_type_defaults:
            leave_type, created = LeaveType.objects.get_or_create(
                name=leave_type_data["name"],
                defaults={
                    "default_days": leave_type_data["default_days"],
                    "requires_attachment": leave_type_data["requires_attachment"],
                    "is_active": leave_type_data["is_active"],
                },
            )

            if not created:
                leave_type.default_days = leave_type_data["default_days"]
                leave_type.requires_attachment = leave_type_data["requires_attachment"]
                leave_type.is_active = leave_type_data["is_active"]
                leave_type.save()

            created_leave_types.append(leave_type)

        users = User.objects.filter(is_active=True)

        balances_created = 0
        balances_already_exist = 0

        for user in users:
            for leave_type in created_leave_types:
                _, created = LeaveBalance.objects.get_or_create(
                    employee=user,
                    leave_type=leave_type,
                    defaults={
                        "total_days": leave_type.default_days,
                        "used_days": 0,
                    },
                )

                if created:
                    balances_created += 1
                else:
                    balances_already_exist += 1

        self.stdout.write(self.style.SUCCESS("Leave types seeded successfully."))
        self.stdout.write(self.style.SUCCESS(f"Users processed: {users.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Leave balances created: {balances_created}"))
        self.stdout.write(self.style.WARNING(f"Leave balances already existing: {balances_already_exist}"))