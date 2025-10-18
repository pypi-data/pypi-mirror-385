"""
User Activity Admin v2.0 - NEW Declarative Pydantic Approach

Enhanced activity tracking with Material Icons and clean declarative config.
"""

from django.contrib import admin

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

from ..models import UserActivity
from .filters import ActivityTypeFilter


# ===== UserActivity Admin =====

useractivity_config = AdminConfig(
    model=UserActivity,

    # Performance optimization
    select_related=["user"],

    # List display
    list_display=[
        "user",
        "activity_type",
        "description",
        "ip_address",
        "created_at"
    ],

    # Display fields with UI widgets
    display_fields=[
        FieldConfig(
            name="user",
            title="User",
            ui_widget="user_avatar",
            header=True
        ),
        FieldConfig(
            name="created_at",
            title="When",
            ui_widget="datetime_relative",
            ordering="created_at"
        ),
    ],

    # Filters and search
    list_filter=[ActivityTypeFilter, "activity_type", "created_at"],
    search_fields=["user__username", "user__email", "description", "ip_address"],

    # Readonly fields
    readonly_fields=["created_at"],

    # Date hierarchy
    date_hierarchy="created_at",

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Activity",
            fields=["user", "activity_type", "description"]
        ),
        FieldsetConfig(
            title="Related Object",
            fields=["object_id", "object_type"],
            collapsed=True,
            description="Optional reference to related model instance"
        ),
        FieldsetConfig(
            title="Request Info",
            fields=["ip_address", "user_agent"],
            collapsed=True
        ),
        FieldsetConfig(
            title="Timestamp",
            fields=["created_at"]
        ),
    ],

    # Ordering
    ordering=["-created_at"],
)


@admin.register(UserActivity)
class UserActivityAdmin(PydanticAdmin):
    """
    UserActivity admin using NEW Pydantic declarative approach.

    Features:
    - Clean declarative config
    - Activity-specific icons and colors
    - Optimized queries with select_related
    """
    config = useractivity_config

    # Custom display methods using decorators
    @computed_field("Activity")
    def activity_type(self, obj):
        """Activity type with appropriate icons and colors."""
        activity_icons = {
            'login': Icons.LOGIN,
            'logout': Icons.LOGOUT,
            'otp_requested': Icons.EMAIL,
            'otp_verified': Icons.VERIFIED,
            'profile_updated': Icons.EDIT,
            'registration': Icons.PERSON_ADD,
        }

        activity_variants = {
            'login': 'success',
            'logout': 'info',
            'otp_requested': 'warning',
            'otp_verified': 'success',
            'profile_updated': 'info',
            'registration': 'primary',
        }

        icon = activity_icons.get(obj.activity_type, Icons.DESCRIPTION)
        variant = activity_variants.get(obj.activity_type, 'info')

        config = StatusBadgeConfig(
            show_icons=True,
            icon=icon,
            custom_mappings={obj.get_activity_type_display(): variant}
        )

        return StatusBadge.create(
            text=obj.get_activity_type_display(),
            variant=variant,
            config=config
        )

    @computed_field("Description")
    def description(self, obj):
        """Truncated description with icon."""
        description = obj.description

        if len(description) > 50:
            description = f"{description[:47]}..."
            variant = "secondary"
        else:
            variant = "info"

        config = StatusBadgeConfig(show_icons=True, icon=Icons.DESCRIPTION)
        return StatusBadge.create(
            text=description,
            variant=variant,
            config=config
        )

    @computed_field("IP Address")
    def ip_address(self, obj):
        """IP address with network icon."""
        if not obj.ip_address:
            return None

        config = StatusBadgeConfig(show_icons=True, icon=Icons.PUBLIC)
        return StatusBadge.create(
            text=obj.ip_address,
            variant="secondary",
            config=config
        )
