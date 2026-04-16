from django.core.exceptions import ValidationError
from django.db import transaction
from datetime import date

from leave_management.models import LeaveBalance, LeaveRequest, LeaveRequestStatus, LeaveType
from leave_management.serializers.base_serializer import LeaveRequestCreateSerializer


@transaction.atomic
def create_leave_request_helper(user, validated_data):
    leave_type_id = validated_data["leave_type_id"]
    start_date = validated_data["start_date"]
    end_date = validated_data["end_date"]
    reason = validated_data.get("reason", "")
    attachment = validated_data.get("attachment")

    try:
        leave_type = LeaveType.objects.get(id=leave_type_id, is_active=True)
    except LeaveType.DoesNotExist:
        raise ValidationError("Selected leave type does not exist or is inactive.")

    if leave_type.requires_attachment and not attachment:
        raise ValidationError({"attachment": ["This leave type requires an attachment."]})

    days_requested = LeaveRequestCreateSerializer.calculate_leave_days(
        start_date=start_date,
        end_date=end_date,
    )

    if days_requested <= 0:
        raise ValidationError("Days requested must be greater than zero.")

    balance = LeaveBalance.objects.select_for_update().filter(
        employee=user,
        leave_type=leave_type,
    ).first()

    if balance is None:
        raise ValidationError("Leave balance does not exist for this user and leave type.")

    if balance.remaining_days < days_requested:
        raise ValidationError("Insufficient leave balance.")

    overlapping_requests = LeaveRequest.objects.filter(
        employee=user,
        start_date__lte=end_date,
        end_date__gte=start_date,
        status__in=[
            LeaveRequestStatus.PENDING,
            LeaveRequestStatus.APPROVED,
        ],
    )

    if overlapping_requests.exists():
        raise ValidationError("This leave request overlaps with an existing request.")

    leave_request = LeaveRequest(
        employee=user,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        days_requested=days_requested,
        reason=reason,
        attachment=attachment,
        status=LeaveRequestStatus.PENDING,
    )

    leave_request.full_clean()
    leave_request.save()

    return leave_request


@transaction.atomic
def cancel_leave_request_helper(user, leave_request_id, cancellation_reason=""):
    try:
        leave_request = LeaveRequest.objects.select_for_update().get(
            id=leave_request_id,
            employee=user
        )
    except LeaveRequest.DoesNotExist:
        raise ValidationError("Leave request not found or does not belong to the user.")

    if leave_request.status == LeaveRequestStatus.CANCELLED:
        raise ValidationError("This leave request is already cancelled.")

    if leave_request.status == LeaveRequestStatus.REJECTED:
        raise ValidationError("Rejected leave requests cannot be cancelled.")

    today = date.today()
    if leave_request.start_date <= today:
        raise ValidationError("Cannot cancel a leave request that has already started.")

    cancellation_reason = (cancellation_reason or "").strip()

    # Optional for PENDING
    if leave_request.status == LeaveRequestStatus.PENDING:
        leave_request.status = LeaveRequestStatus.CANCELLED
        leave_request.cancellation_reason = cancellation_reason
        leave_request.save(update_fields=["status", "cancellation_reason", "updated_at"])
        return leave_request

    # Required for APPROVED
    if leave_request.status == LeaveRequestStatus.APPROVED:
        if not cancellation_reason:
            raise ValidationError("Cancellation reason is required for approved leave requests.")

        balance = LeaveBalance.objects.select_for_update().get(
            employee=user,
            leave_type=leave_request.leave_type
        )
        balance.used_days -= leave_request.days_requested
        balance.full_clean()
        balance.save()

        leave_request.status = LeaveRequestStatus.CANCELLED
        leave_request.cancellation_reason = cancellation_reason
        leave_request.approved_by = None
        leave_request.approved_at = None
        leave_request.save(
            update_fields=[
                "status",
                "cancellation_reason",
                "approved_by",
                "approved_at",
                "updated_at",
            ]
        )
        return leave_request

    raise ValidationError("This leave request cannot be cancelled.")