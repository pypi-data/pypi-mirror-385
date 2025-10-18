"""
Group Admin v2.0 - NEW Declarative Pydantic Approach

Enhanced group management with Material Icons and clean declarative config.
"""

from django.contrib import admin
from django.contrib.auth.models import Group

from django_cfg.modules.django_admin import (
    AdminConfig,
    FieldConfig,
    FieldsetConfig,
    Icons,
    computed_field,
)
from django_cfg.modules.django_admin.base import PydanticAdmin
from django_cfg.modules.django_admin.utils.badges import StatusBadge
from django_cfg.modules.django_admin.models.badge_models import StatusBadgeConfig


# ===== Group Admin =====

group_config = AdminConfig(
    model=Group,

    # List display
    list_display=[
        "name",
        "users_count",
        "permissions_count"
    ],

    # Display fields with UI widgets
    display_fields=[
        FieldConfig(
            name="name",
            title="Group Name",
            ui_widget="badge",
            variant="primary",
            icon=Icons.GROUP,
            ordering="name"
        ),
    ],

    # Search
    search_fields=["name"],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Group Details",
            fields=["name"]
        ),
        FieldsetConfig(
            title="Permissions",
            fields=["permissions"],
            collapsed=True
        ),
    ],

    # Ordering
    ordering=["name"],
)


class GroupAdmin(PydanticAdmin):
    """
    Group admin using NEW Pydantic declarative approach.

    Features:
    - Clean declarative config
    - User and permission counts
    - Material Icons integration
    """
    config = group_config

    # Django-specific field
    filter_horizontal = ['permissions']

    # Custom display methods using decorators
    @computed_field("Users")
    def users_count(self, obj):
        """Count of users in this group."""
        count = obj.user_set.count()
        if count == 0:
            return None

        config = StatusBadgeConfig(show_icons=True, icon=Icons.PEOPLE)
        return StatusBadge.create(
            text=f"{count} user{'s' if count != 1 else ''}",
            variant="info",
            config=config
        )

    @computed_field("Permissions")
    def permissions_count(self, obj):
        """Count of permissions in this group."""
        count = obj.permissions.count()

        config = StatusBadgeConfig(show_icons=True, icon=Icons.SECURITY)

        if count == 0:
            return StatusBadge.create(
                text="No permissions",
                variant="secondary",
                config=config
            )

        return StatusBadge.create(
            text=f"{count} permission{'s' if count != 1 else ''}",
            variant="warning",
            config=config
        )
