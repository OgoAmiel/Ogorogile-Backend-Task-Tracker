from django.shortcuts import render
from django.core.exceptions import ValidationError as DjangoValidationError
from leave_management.api_helpers.leave_helpers import create_leave_request_helper, cancel_leave_request_helper
from leave_management.models import LeaveBalance, LeaveRequest
from leave_management.serializers.model_serializer import LeaveBalanceSerializer, LeaveRequestListSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from leave_management.serializers.base_serializer import CancelLeaveRequestSerializer, LeaveRequestCreateSerializer

# Create your views here.
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_leave_request(request):
    serializer = LeaveRequestCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            "status": "error",
            "message": serializer.errors,},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        leave_request = create_leave_request_helper(
            user=request.user,
            validated_data=serializer.validated_data,
        )

        return Response({
            "status": "success",
            "message": "Leave request created successfully",
            "data": LeaveRequestListSerializer(leave_request).data,},
            status=status.HTTP_201_CREATED,
        )

    except DjangoValidationError as error:
        return Response({
            "status": "error",
            "message": error.message_dict if hasattr(error, "message_dict") else error.messages,},
            status=status.HTTP_400_BAD_REQUEST,
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_leave_requests(request):
    try:
        leave_requests = LeaveRequest.objects.filter(
            employee=request.user
            ).select_related("employee", "leave_type", "approved_by")

        serializer = LeaveRequestListSerializer(leave_requests, many=True)
        return Response({
            "status": "success",
            "message": "Leave requests retrieved successfully",
            "data": serializer.data,},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),},
            status=status.HTTP_400_BAD_REQUEST,
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_leave_balances(request):
    try:
        leave_balances = LeaveBalance.objects.filter(
            employee=request.user
            ).select_related("leave_type")

        serializer = LeaveBalanceSerializer(leave_balances, many=True)
        return Response({
            "status": "success",
            "message": "Leave balances retrieved successfully",
            "data": serializer.data,},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),},
            status=status.HTTP_400_BAD_REQUEST,
        )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_leave_request(request):
    serializer = CancelLeaveRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            "status": "error",
            "message": serializer.errors,},
            status=status.HTTP_400_BAD_REQUEST,
        )

    leave_request_id = serializer.validated_data.get("leave_request_id")
    cancellation_reason = serializer.validated_data.get("cancellation_reason", "")

    try:
        leave_request = cancel_leave_request_helper(
            user=request.user,
            leave_request_id=leave_request_id,
            cancellation_reason=cancellation_reason,
        )

        return Response({
            "status": "success",
            "message": "Leave request cancelled successfully",
            "data": LeaveRequestListSerializer(leave_request).data,},
            status=status.HTTP_200_OK,
        )

    except DjangoValidationError as error:
        return Response({
            "status": "error",
            "message": error.message_dict if hasattr(error, "message_dict") else error.messages,},
            status=status.HTTP_400_BAD_REQUEST,
        )