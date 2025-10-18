"""
Currency Admin v2.0 - NEW Declarative Pydantic Approach (TEST)

Testing new django_admin module with real Currency model.
"""

from django.contrib import admin

from django_cfg.modules.django_admin import (
    ActionConfig,
    AdminConfig,
    FieldConfig,
    FieldsetConfig,
    Icons,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import Currency

# ✅ Declarative Pydantic Config
currency_config = AdminConfig(
    model=Currency,

    list_display=[
        "code",
        "name",
        "token",
        "network",
        "is_active",
        "sort_order",
        "updated_at"
    ],

    display_fields=[
        FieldConfig(
            name="code",
            title="Code",
            ui_widget="badge",
            variant="primary",
            icon=Icons.CURRENCY_BITCOIN
        ),
        FieldConfig(
            name="name",
            title="Name",
            ui_widget="text"
        ),
        FieldConfig(
            name="token",
            title="Token",
            ui_widget="badge",
            variant="info",
            icon=Icons.ATTACH_MONEY
        ),
        FieldConfig(
            name="network",
            title="Network",
            ui_widget="badge",
            variant="warning",
            icon=Icons.CLOUD,
            empty_value="N/A"
        ),
        FieldConfig(
            name="is_active",
            title="Status",
            ui_widget="badge",
            label_map={
                "True": "success",
                "False": "secondary"
            },
            boolean=True
        ),
        FieldConfig(
            name="sort_order",
            title="Sort Order",
            ui_widget="text"
        ),
        FieldConfig(
            name="updated_at",
            title="Updated",
            ui_widget="datetime_relative",
            ordering="updated_at"
        ),
    ],

    list_filter=[
        "is_active",
        "token",
        "network",
        "updated_at"
    ],

    search_fields=["code", "name", "token", "network"],
    readonly_fields=["created_at", "updated_at"],

    fieldsets=[
        FieldsetConfig(
            title="Currency Information",
            fields=["code", "name", "token", "network", "symbol"]
        ),
        FieldsetConfig(
            title="Provider Settings",
            fields=["provider", "min_amount_usd", "decimal_places"]
        ),
        FieldsetConfig(
            title="Display Settings",
            fields=["is_active", "sort_order"]
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at"],
            collapsed=True
        ),
    ],

    actions=[
        ActionConfig(
            name="activate_currencies",
            description="Activate currencies",
            variant="success",
            handler="django_cfg.apps.payments.admin.actions.activate_currencies"
        ),
        ActionConfig(
            name="deactivate_currencies",
            description="Deactivate currencies",
            variant="warning",
            handler="django_cfg.apps.payments.admin.actions.deactivate_currencies"
        )
    ],

    ordering=["code"],
    list_per_page=100
)

# ✅ Minimal Admin Class
@admin.register(Currency)
class CurrencyAdmin(PydanticAdmin):
    """Currency admin using NEW Pydantic declarative approach."""
    config = currency_config
