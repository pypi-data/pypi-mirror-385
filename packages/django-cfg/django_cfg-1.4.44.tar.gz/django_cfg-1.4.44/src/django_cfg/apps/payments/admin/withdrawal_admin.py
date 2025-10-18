"""
Withdrawal Admin v2.0 - NEW Declarative Pydantic Approach

Manual approval workflow for withdrawal requests with clean declarative config.
"""

from django.contrib import admin
from django.utils.html import format_html

from django_cfg.modules.django_admin import (
    ActionConfig,
    AdminConfig,
    FieldConfig,
    FieldsetConfig,
    Icons,
    computed_field,
)
from django_cfg.modules.django_admin.base import PydanticAdmin
from django_cfg.modules.django_admin.utils.badges import StatusBadge
from django_cfg.modules.django_admin.models.badge_models import StatusBadgeConfig

from ..models import WithdrawalRequest
from .filters import RecentActivityFilter, WithdrawalStatusFilter


# ===== WithdrawalRequest Admin =====

withdrawalrequest_config = AdminConfig(
    model=WithdrawalRequest,

    # Performance optimization
    select_related=["user", "currency", "admin_user"],

    # List display
    list_display=[
        "withdrawal_id",
        "user",
        "amount_usd",
        "currency",
        "status",
        "admin_user",
        "created_at"
    ],

    # Display fields with UI widgets
    display_fields=[
        FieldConfig(
            name="withdrawal_id",
            title="Withdrawal ID",
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
            precision=2,
            ordering="amount_usd"
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
                "approved": "info",
                "processing": "primary",
                "completed": "success",
                "rejected": "danger",
                "cancelled": "secondary"
            },
            ordering="status"
        ),
        FieldConfig(
            name="admin_user",
            title="Admin",
            ui_widget="text",
            empty_value="—"
        ),
        FieldConfig(
            name="created_at",
            title="Created",
            ui_widget="datetime_relative",
            ordering="created_at"
        ),
    ],

    # Filters and search
    list_filter=[
        WithdrawalStatusFilter,
        RecentActivityFilter,
        "currency",
        "status",
        "created_at"
    ],

    search_fields=[
        "id",
        "internal_withdrawal_id",
        "user__username",
        "user__email",
        "wallet_address",
        "admin_user__username"
    ],

    # Readonly fields
    readonly_fields=[
        "id",
        "internal_withdrawal_id",
        "created_at",
        "updated_at",
        "approved_at",
        "completed_at",
        "rejected_at",
        "cancelled_at",
        "status_changed_at",
        "withdrawal_details_display"
    ],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Request Information",
            fields=[
                "id",
                "internal_withdrawal_id",
                "user",
                "status",
                "amount_usd",
                "currency",
                "wallet_address"
            ]
        ),
        FieldsetConfig(
            title="Fee Calculation",
            fields=[
                "network_fee_usd",
                "service_fee_usd",
                "total_fee_usd",
                "final_amount_usd"
            ],
            collapsed=True
        ),
        FieldsetConfig(
            title="Admin Actions",
            fields=[
                "admin_user",
                "admin_notes"
            ]
        ),
        FieldsetConfig(
            title="Transaction Details",
            fields=[
                "transaction_hash",
                "crypto_amount"
            ],
            collapsed=True
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=[
                "created_at",
                "updated_at",
                "approved_at",
                "completed_at",
                "rejected_at",
                "cancelled_at",
                "status_changed_at"
            ],
            collapsed=True
        ),
        FieldsetConfig(
            title="Withdrawal Details",
            fields=["withdrawal_details_display"],
            collapsed=True
        )
    ],

    # Actions
    actions=[
        ActionConfig(
            name="approve_withdrawals",
            description="Approve withdrawals",
            variant="success",
            handler="django_cfg.apps.payments.admin.withdrawal_actions.approve_withdrawals"
        ),
        ActionConfig(
            name="reject_withdrawals",
            description="Reject withdrawals",
            variant="danger",
            handler="django_cfg.apps.payments.admin.withdrawal_actions.reject_withdrawals"
        ),
        ActionConfig(
            name="mark_as_completed",
            description="Mark as completed",
            variant="success",
            handler="django_cfg.apps.payments.admin.withdrawal_actions.mark_as_completed"
        ),
    ],

    # Ordering
    ordering=["-created_at"],
)


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(PydanticAdmin):
    """
    Withdrawal Request admin for Payments v2.0 using NEW Pydantic declarative approach.

    Features:
    - Manual approval workflow
    - Admin tracking
    - Status management
    - Clean declarative config
    """
    config = withdrawalrequest_config

    # Custom display methods using decorators
    @computed_field("Withdrawal ID")
    def withdrawal_id(self, obj):
        """Withdrawal ID display with badge."""
        # Show internal_withdrawal_id if available, otherwise use UUID
        withdrawal_id = obj.internal_withdrawal_id if obj.internal_withdrawal_id else str(obj.id)[:16]
        return StatusBadge.create(
            text=withdrawal_id,
            variant="info"
        )

    @computed_field("Currency")
    def currency(self, obj):
        """Currency display with token+network."""
        if not obj.currency:
            return StatusBadge.create(text="N/A", variant="secondary")

        # Display token and network
        text = obj.currency.token
        if obj.currency.network:
            text += f" ({obj.currency.network})"

        config = StatusBadgeConfig(show_icons=True, icon=Icons.CURRENCY_BITCOIN)
        return StatusBadge.create(text=text, variant="primary", config=config)

    # Readonly field displays
    def withdrawal_details_display(self, obj):
        """Detailed withdrawal information for detail view."""
        if not obj.pk:
            return "Save to see details"

        # Build details HTML
        details = []

        details.append(f"<strong>Withdrawal ID:</strong> {obj.id}")
        details.append(f"<strong>User:</strong> {obj.user.username} ({obj.user.email})")
        details.append(f"<strong>Amount:</strong> ${obj.amount_usd:.2f} USD")
        details.append(f"<strong>Currency:</strong> {obj.currency.code}")
        details.append(f"<strong>Wallet Address:</strong> <code>{obj.wallet_address}</code>")
        details.append(f"<strong>Status:</strong> {obj.get_status_display()}")

        if obj.network_fee_usd:
            details.append(f"<strong>Network Fee:</strong> ${obj.network_fee_usd:.2f} USD")

        if obj.service_fee_usd:
            details.append(f"<strong>Service Fee:</strong> ${obj.service_fee_usd:.2f} USD")

        if obj.total_fee_usd:
            details.append(f"<strong>Total Fee:</strong> ${obj.total_fee_usd:.2f} USD")

        if obj.final_amount_usd:
            details.append(f"<strong>Final Amount:</strong> ${obj.final_amount_usd:.2f} USD")

        if obj.admin_user:
            details.append(f"<strong>Approved By:</strong> {obj.admin_user.username}")

        if obj.admin_notes:
            details.append(f"<strong>Admin Notes:</strong> {obj.admin_notes}")

        if obj.transaction_hash:
            details.append(f"<strong>Transaction Hash:</strong> <code>{obj.transaction_hash}</code>")

        if obj.crypto_amount:
            details.append(f"<strong>Crypto Amount:</strong> {obj.crypto_amount:.8f} {obj.currency.token}")

        if obj.approved_at:
            details.append(f"<strong>Approved At:</strong> {obj.approved_at}")

        if obj.completed_at:
            details.append(f"<strong>Completed At:</strong> {obj.completed_at}")

        if obj.rejected_at:
            details.append(f"<strong>Rejected At:</strong> {obj.rejected_at}")

        return format_html("<br>".join(details))

    withdrawal_details_display.short_description = "Withdrawal Details"
