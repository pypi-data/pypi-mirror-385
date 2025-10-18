"""
Payment Admin v2.0 - NEW Declarative Pydantic Approach

Clean, modern payment management using Unfold Admin with declarative config.
"""

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from django_cfg.modules.django_admin import (
    ActionConfig,
    AdminConfig,
    FieldConfig,
    FieldsetConfig,
    Icons,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import Payment
from .filters import PaymentAmountFilter, PaymentStatusFilter, RecentActivityFilter

# ✅ Declarative Pydantic Config
payment_config = AdminConfig(
    model=Payment,

    # Performance optimization
    select_related=["user", "currency"],

    # List display
    list_display=[
        "internal_payment_id",
        "user",
        "amount_usd",
        "currency",
        "status",
        "status_changed_at",
        "created_at"
    ],

    # Display fields with UI widgets
    display_fields=[
        FieldConfig(
            name="internal_payment_id",
            title="Payment ID",
            ui_widget="badge",
            variant="info",
            icon=Icons.RECEIPT
        ),
        FieldConfig(
            name="user",
            title="User",
            ui_widget="user_avatar",
            header=True
        ),
        FieldConfig(
            name="amount_usd",
            title="Amount",
            ui_widget="currency",
            currency="USD",
            precision=2
        ),
        FieldConfig(
            name="currency",
            title="Currency",
            ui_widget="text"
        ),
        FieldConfig(
            name="status",
            title="Status",
            ui_widget="badge",
            label_map={
                "pending": "warning",
                "confirming": "info",
                "confirmed": "primary",
                "completed": "success",
                "partially_paid": "warning",
                "failed": "danger",
                "cancelled": "secondary",
                "expired": "danger"
            }
        ),
        FieldConfig(
            name="status_changed_at",
            title="Status Changed",
            ui_widget="datetime_relative",
            ordering="status_changed_at",
            empty_value="-"
        ),
        FieldConfig(
            name="created_at",
            title="Created",
            ui_widget="datetime_relative",
            ordering="created_at"
        ),
    ],

    # Filters
    list_filter=[
        PaymentStatusFilter,
        PaymentAmountFilter,
        RecentActivityFilter,
        "currency",
        "created_at",
        "status_changed_at",
    ],

    # Search
    search_fields=[
        "internal_payment_id",
        "provider_payment_id",
        "transaction_hash",
        "user__username",
        "user__email",
        "pay_address"
    ],

    # Readonly fields
    readonly_fields=[
        "id",
        "internal_payment_id",
        "provider_payment_id",
        "created_at",
        "updated_at",
        "status_changed_at",
        "completed_at",
        "payment_details_display",
        "qr_code_display",
    ],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Basic Information",
            fields=["id", "internal_payment_id", "user", "status", "description"]
        ),
        FieldsetConfig(
            title="Payment Details",
            fields=["amount_usd", "currency", "pay_amount", "actual_amount", "actual_amount_usd"]
        ),
        FieldsetConfig(
            title="Provider Information",
            fields=["provider", "provider_payment_id", "pay_address", "payment_url"]
        ),
        FieldsetConfig(
            title="Blockchain Information",
            fields=["transaction_hash", "confirmations_count"],
            collapsed=True
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at", "status_changed_at", "completed_at", "expires_at"],
            collapsed=True
        ),
        FieldsetConfig(
            title="Additional Info",
            fields=["provider_data", "payment_details_display", "qr_code_display"],
            collapsed=True
        ),
    ],

    # Actions
    actions=[
        ActionConfig(
            name="mark_as_completed",
            description="Mark as completed",
            variant="success",
            handler="django_cfg.apps.payments.admin.payment_actions.mark_as_completed"
        ),
        ActionConfig(
            name="mark_as_failed",
            description="Mark as failed",
            variant="danger",
            handler="django_cfg.apps.payments.admin.payment_actions.mark_as_failed"
        ),
        ActionConfig(
            name="cancel_payments",
            description="Cancel payments",
            variant="warning",
            handler="django_cfg.apps.payments.admin.payment_actions.cancel_payments"
        ),
    ],

    # Ordering
    ordering=["-created_at"],
    list_per_page=50
)


# ✅ Minimal Admin Class with Custom Readonly Methods
@admin.register(Payment)
class PaymentAdmin(PydanticAdmin):
    """
    Payment admin for Payments v2.0 using NEW Pydantic declarative approach.

    Features:
    - Declarative configuration with type safety
    - Automatic display method generation
    - Clean UI with Unfold theme
    - NowPayments-specific status handling
    - Custom readonly fields for detail view
    """
    config = payment_config

    # Custom readonly field methods (not auto-generated)
    def payment_details_display(self, obj):
        """Detailed payment information for detail view."""
        if not obj.pk:
            return "Save to see details"

        # Calculate age
        age = timezone.now() - obj.created_at
        age_text = f"{age.days} days, {age.seconds // 3600} hours"

        # Build details HTML
        details = []

        # Basic info
        details.append(f"<strong>Internal ID:</strong> {obj.internal_payment_id}")
        details.append(f"<strong>Age:</strong> {age_text}")

        # Provider info
        if obj.provider_payment_id:
            details.append(f"<strong>Provider Payment ID:</strong> {obj.provider_payment_id}")

        # Transaction details
        if obj.transaction_hash:
            explorer_link = obj.get_explorer_link()
            if explorer_link:
                details.append(f"<strong>Transaction:</strong> <a href='{explorer_link}' target='_blank'>{obj.transaction_hash[:16]}...</a>")
            else:
                details.append(f"<strong>Transaction Hash:</strong> {obj.transaction_hash}")

        if obj.confirmations_count > 0:
            details.append(f"<strong>Confirmations:</strong> {obj.confirmations_count}")

        if obj.pay_address:
            details.append(f"<strong>Pay Address:</strong> <code>{obj.pay_address}</code>")

        if obj.pay_amount:
            details.append(f"<strong>Pay Amount:</strong> {obj.pay_amount:.8f} {obj.currency.token}")

        if obj.actual_amount:
            details.append(f"<strong>Actual Amount:</strong> {obj.actual_amount:.8f} {obj.currency.token}")

        # URLs
        if obj.payment_url:
            details.append(f"<strong>Payment URL:</strong> <a href='{obj.payment_url}' target='_blank'>Open</a>")

        # Expiration
        if obj.expires_at:
            if obj.is_expired:
                details.append(f"<strong>Expired:</strong> <span style='color:red;'>Yes ({obj.expires_at})</span>")
            else:
                details.append(f"<strong>Expires At:</strong> {obj.expires_at}")

        # Description
        if obj.description:
            details.append(f"<strong>Description:</strong> {obj.description}")

        return format_html("<br>".join(details))

    payment_details_display.short_description = "Payment Details"

    def qr_code_display(self, obj):
        """QR code display for payment address."""
        if not obj.pay_address:
            return "No payment address"

        qr_url = obj.get_qr_code_url(size=200)
        if qr_url:
            return format_html(
                '<img src="{}" alt="QR Code" style="max-width:200px;"><br>'
                '<small>Scan to pay: <code>{}</code></small>',
                qr_url,
                obj.pay_address
            )
        return f"Address: {obj.pay_address}"

    qr_code_display.short_description = "QR Code"
