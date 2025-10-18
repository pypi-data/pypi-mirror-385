"""
Toolsets Admin v2.0 - NEW Declarative Pydantic Approach

Enhanced toolset management with Material Icons and clean declarative config.
"""

from datetime import timedelta

from django.contrib import admin, messages
from django.db import models
from django.db.models.fields.json import JSONField
from django.utils import timezone
from django_json_widget.widgets import JSONEditorWidget
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import AutocompleteSelectFilter
from unfold.contrib.forms.widgets import WysiwygWidget

from django_cfg import ExportForm
from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    TextField,
    UserField,
    DateTimeField,
    FieldsetConfig,
    Icons,
    computed_field,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models.toolsets import ApprovalLog, ToolExecution, ToolsetConfiguration


# ===== Tool Execution Admin Config =====

tool_execution_config = AdminConfig(
    model=ToolExecution,

    # Performance optimization
    select_related=['agent_execution', 'user'],

    # Import/Export
    import_export_enabled=True,

    # List display
    list_display=[
        'id_display',
        'tool_name_display',
        'toolset_display',
        'status_display',
        'duration_display',
        'retry_count_display',
        'created_at_display'
    ],

    # Display fields with UI widgets
    display_fields=[
        BadgeField(
            name="id",
            title="ID",
            variant="secondary",
            icon=Icons.TAG,
            header=True
        ),
        BadgeField(
            name="tool_name",
            title="Tool",
            variant="primary",
            icon=Icons.BUILD
        ),
        BadgeField(
            name="toolset_class",
            title="Toolset",
            variant="info",
            icon=Icons.EXTENSION
        ),
        BadgeField(
            name="status",
            title="Status"
        ),
        TextField(
            name="execution_time",
            title="Duration"
        ),
        BadgeField(
            name="retry_count",
            title="Retries",
            variant="warning",
            icon=Icons.REFRESH
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
    ],

    # Search and filters
    search_fields=['tool_name', 'toolset_name', 'arguments', 'result'],
    list_filter=['status', 'tool_name', 'created_at'],

    # Ordering
    ordering=['-created_at'],
)


@admin.register(ToolExecution)
class ToolExecutionAdmin(PydanticAdmin):
    """
    Tool Execution admin using NEW Pydantic declarative approach.

    Features:
    - Declarative configuration with type safety
    - Automatic display method generation
    - Material Icons integration
    - Export functionality (via config)
    - Retry and error management actions
    """
    config = tool_execution_config

    # Override list_display_links
    list_display_links = ['id_display', 'tool_name_display']

    # Override list_filter to add custom filters
    list_filter = ['status', 'tool_name', 'created_at', ('agent_execution', AutocompleteSelectFilter)]

    # Autocomplete
    autocomplete_fields = ['agent_execution']

    # Readonly fields
    readonly_fields = ['id', 'execution_time', 'retry_count', 'created_at', 'started_at', 'completed_at']

    # Unfold form field overrides
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget},
    }

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="Tool Info",
            fields=['id', 'tool_name', 'toolset_class', 'agent_execution']
        ),
        FieldsetConfig(
            title="Execution Data",
            fields=['arguments', 'result', 'error_message']
        ),
        FieldsetConfig(
            title="Metrics",
            fields=['execution_time', 'retry_count', 'status']
        ),
        FieldsetConfig(
            title="Approval",
            fields=['approval_log'],
            collapsed=True
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=['created_at', 'started_at', 'completed_at'],
            collapsed=True
        ),
    ]

    # Actions
    actions = ['retry_failed_executions', 'clear_errors']

    # Custom display methods using @computed_field decorator
    @computed_field("ID")
    def id_display(self, obj: ToolExecution) -> str:
        """Enhanced ID display."""
        return self.html.badge(f"#{str(obj.id)[:8]}", variant="secondary", icon=Icons.TAG)

    @computed_field("Tool")
    def tool_name_display(self, obj: ToolExecution) -> str:
        """Enhanced tool name display."""
        return self.html.badge(obj.tool_name, variant="primary", icon=Icons.BUILD)

    @computed_field("Toolset")
    def toolset_display(self, obj: ToolExecution) -> str:
        """Toolset class display with badge."""
        if not obj.toolset_class:
            return "—"

        # Extract class name from full path
        class_name = obj.toolset_class.split('.')[-1] if '.' in obj.toolset_class else obj.toolset_class

        return self.html.badge(class_name, variant="info", icon=Icons.EXTENSION)

    @computed_field("Status")
    def status_display(self, obj: ToolExecution) -> str:
        """Status display with appropriate icons."""
        icon_map = {
            'running': Icons.PLAY_ARROW,
            'completed': Icons.CHECK_CIRCLE,
            'failed': Icons.ERROR,
            'pending': Icons.SCHEDULE,
            'cancelled': Icons.CANCEL
        }

        variant_map = {
            'pending': 'warning',
            'running': 'info',
            'completed': 'success',
            'failed': 'danger',
            'cancelled': 'secondary'
        }

        icon = icon_map.get(obj.status, Icons.SCHEDULE)
        variant = variant_map.get(obj.status, 'warning')
        text = obj.get_status_display() if hasattr(obj, 'get_status_display') else obj.status.title()
        return self.html.badge(text, variant=variant, icon=icon)

    @computed_field("Duration")
    def duration_display(self, obj: ToolExecution) -> str:
        """Execution duration display."""
        if obj.execution_time:
            return f"{obj.execution_time:.3f}s"
        return "—"

    @computed_field("Retries")
    def retry_count_display(self, obj: ToolExecution) -> str:
        """Retry count display with badge."""
        if obj.retry_count > 0:
            variant = "warning" if obj.retry_count > 2 else "info"
            return self.html.badge(str(obj.retry_count), variant=variant
            )
        return "0"

    @computed_field("Created")
    def created_at_display(self, obj: ToolExecution) -> str:
        """Created time with relative display."""
        # DateTimeField in display_fields handles formatting automatically
        return obj.created_at

    # Old-style actions (TODO: Migrate to new ActionConfig system when available)
    def retry_failed_executions(self, request, queryset):
        """Retry failed tool executions."""
        failed_count = queryset.filter(status='failed').count()
        messages.warning(request, f"Retry functionality not implemented yet. {failed_count} failed executions selected.")
    retry_failed_executions.short_description = "Retry failed executions"

    def clear_errors(self, request, queryset):
        """Clear error messages from executions."""
        updated = queryset.update(error_message=None)
        messages.info(request, f"Cleared error messages from {updated} executions.")
    clear_errors.short_description = "Clear error messages"


# ===== Approval Log Admin Config =====

approval_log_config = AdminConfig(
    model=ApprovalLog,

    # Performance optimization
    select_related=['approved_by'],

    # Import/Export
    import_export_enabled=True,

    # List display
    list_display=[
        'approval_id_display',
        'tool_name_display',
        'status_display',
        'approved_by_display',
        'decision_time_display',
        'expires_at_display'
    ],

    # Display fields with UI widgets
    display_fields=[
        BadgeField(
            name="id",
            title="Approval ID",
            variant="secondary",
            icon=Icons.VERIFIED,
            header=True
        ),
        BadgeField(
            name="tool_name",
            title="Tool",
            variant="primary",
            icon=Icons.BUILD
        ),
        BadgeField(
            name="status",
            title="Status"
        ),
        UserField(
            name="approved_by",
            title="Approved By"
        ),
        TextField(
            name="decision_time",
            title="Decision Time"
        ),
        DateTimeField(
            name="expires_at",
            title="Expires"
        ),
    ],

    # Search and filters
    search_fields=['tool_name', 'tool_args', 'justification'],
    list_filter=['status', 'tool_name', 'requested_at', 'expires_at'],

    # Ordering
    ordering=['-requested_at'],
)


@admin.register(ApprovalLog)
class ApprovalLogAdmin(PydanticAdmin):
    """
    Approval Log admin using NEW Pydantic declarative approach.

    Features:
    - Declarative configuration with type safety
    - Automatic display method generation
    - Material Icons integration
    - Export functionality (via config)
    - Approval management actions
    """
    config = approval_log_config

    # Override list_display_links
    list_display_links = ['approval_id_display', 'tool_name_display']

    # Override list_filter to add custom filters
    list_filter = ['status', 'tool_name', 'requested_at', 'expires_at', ('approved_by', AutocompleteSelectFilter)]

    # Autocomplete
    autocomplete_fields = ['approved_by']

    # Readonly fields
    readonly_fields = ['id', 'requested_at', 'decided_at', 'expires_at']

    # Unfold form field overrides
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget},
    }

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="Approval Info",
            fields=['id', 'tool_name', 'status', 'approved_by']
        ),
        FieldsetConfig(
            title="Request Details",
            fields=['tool_arguments', 'justification']
        ),
        FieldsetConfig(
            title="Timing",
            fields=['created_at', 'decision_time', 'expires_at']
        ),
    ]

    # Actions
    actions = ['approve_pending', 'reject_pending', 'extend_expiry']

    # Custom display methods using @computed_field decorator
    @computed_field("Approval ID")
    def approval_id_display(self, obj: ApprovalLog) -> str:
        """Enhanced approval ID display."""
        return self.html.badge(f"#{str(obj.id)[:8]}", variant="secondary", icon=Icons.VERIFIED)

    @computed_field("Tool")
    def tool_name_display(self, obj: ApprovalLog) -> str:
        """Enhanced tool name display."""
        return self.html.badge(obj.tool_name, variant="primary", icon=Icons.BUILD)

    @computed_field("Status")
    def status_display(self, obj: ApprovalLog) -> str:
        """Status display with appropriate icons."""
        icon_map = {
            'approved': Icons.CHECK_CIRCLE,
            'rejected': Icons.CANCEL,
            'pending': Icons.SCHEDULE,
            'expired': Icons.TIMER_OFF
        }

        variant_map = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'expired': 'secondary'
        }

        icon = icon_map.get(obj.status, Icons.SCHEDULE)
        variant = variant_map.get(obj.status, 'warning')
        text = obj.get_status_display() if hasattr(obj, 'get_status_display') else obj.status.title()
        return self.html.badge(text, variant=variant, icon=icon)

    @computed_field("Approved By")
    def approved_by_display(self, obj: ApprovalLog) -> str:
        """Approved by user display."""
        if not obj.approved_by:
            return "—"
        # Simple username display, UserField handles avatar and styling
        return obj.approved_by.username

    @computed_field("Decision Time")
    def decision_time_display(self, obj: ApprovalLog) -> str:
        """Decision time display."""
        if obj.decision_time:
            return f"{obj.decision_time:.2f}s"
        return "—"

    @computed_field("Expires")
    def expires_at_display(self, obj: ApprovalLog) -> str:
        """Expiry time with relative display."""
        if not obj.expires_at:
            return "—"

        # DateTimeField in display_fields handles formatting automatically
        return obj.expires_at

    # Old-style actions (TODO: Migrate to new ActionConfig system when available)
    def approve_pending(self, request, queryset):
        """Approve pending approvals."""
        updated = queryset.filter(status='pending').update(
            status='approved',
            approved_by=request.user,
            decision_time=timezone.now()
        )
        messages.success(request, f"Approved {updated} pending requests.")
    approve_pending.short_description = "Approve pending"

    def reject_pending(self, request, queryset):
        """Reject pending approvals."""
        updated = queryset.filter(status='pending').update(
            status='rejected',
            approved_by=request.user,
            decision_time=timezone.now()
        )
        messages.warning(request, f"Rejected {updated} pending requests.")
    reject_pending.short_description = "Reject pending"

    def extend_expiry(self, request, queryset):
        """Extend expiry time for pending approvals."""
        new_expiry = timezone.now() + timedelta(hours=24)
        updated = queryset.filter(status='pending').update(expires_at=new_expiry)
        messages.info(request, f"Extended expiry for {updated} approvals by 24 hours.")
    extend_expiry.short_description = "Extend expiry"


# ===== Toolset Configuration Admin Config =====

toolset_config_config = AdminConfig(
    model=ToolsetConfiguration,

    # Performance optimization
    select_related=['created_by'],

    # Import/Export
    import_export_enabled=True,

    # List display
    list_display=[
        'name_display',
        'toolset_class_display',
        'status_display',
        'usage_count_display',
        'created_by_display',
        'created_at_display'
    ],

    # Display fields with UI widgets
    display_fields=[
        BadgeField(
            name="name",
            title="Configuration Name",
            variant="primary",
            icon=Icons.SETTINGS,
            header=True
        ),
        BadgeField(
            name="toolset_class",
            title="Toolset Class",
            variant="info",
            icon=Icons.EXTENSION
        ),
        BadgeField(
            name="is_active",
            title="Status"
        ),
        TextField(
            name="usage_count",
            title="Usage"
        ),
        UserField(
            name="created_by",
            title="Created By"
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
    ],

    # Search and filters
    search_fields=['name', 'description', 'toolset_class'],
    list_filter=['is_active', 'toolset_class', 'created_at'],

    # Ordering
    ordering=['-created_at'],
)


@admin.register(ToolsetConfiguration)
class ToolsetConfigurationAdmin(PydanticAdmin):
    """
    Toolset Configuration admin using NEW Pydantic declarative approach.

    Features:
    - Declarative configuration with type safety
    - Automatic display method generation
    - Material Icons integration
    - Export functionality (via config)
    - Configuration management actions
    """
    config = toolset_config_config

    # Override list_display_links
    list_display_links = ['name_display']

    # Override list_filter to add custom filters
    list_filter = ['is_active', 'toolset_class', 'created_at', ('created_by', AutocompleteSelectFilter)]

    # Autocomplete
    autocomplete_fields = ['created_by']

    # Readonly fields
    readonly_fields = ['id', 'created_at', 'updated_at']

    # Unfold form field overrides
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget},
    }

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="Configuration Info",
            fields=['id', 'name', 'description', 'toolset_class']
        ),
        FieldsetConfig(
            title="Settings",
            fields=['configuration', 'is_active']
        ),
        FieldsetConfig(
            title="Usage",
            fields=['usage_count']
        ),
        FieldsetConfig(
            title="Metadata",
            fields=['created_by', 'updated_by', 'created_at', 'updated_at'],
            collapsed=True
        ),
    ]

    # Actions
    actions = ['activate_configurations', 'deactivate_configurations', 'reset_usage']

    # Custom display methods using @computed_field decorator
    @computed_field("Configuration Name")
    def name_display(self, obj: ToolsetConfiguration) -> str:
        """Enhanced configuration name display."""
        return self.html.badge(obj.name, variant="primary", icon=Icons.SETTINGS)

    @computed_field("Toolset Class")
    def toolset_class_display(self, obj: ToolsetConfiguration) -> str:
        """Toolset class display with badge."""
        if not obj.toolset_class:
            return "—"

        # Extract class name from full path
        class_name = obj.toolset_class.split('.')[-1] if '.' in obj.toolset_class else obj.toolset_class

        return self.html.badge(class_name, variant="info", icon=Icons.EXTENSION)

    @computed_field("Status")
    def status_display(self, obj: ToolsetConfiguration) -> str:
        """Status display based on active state."""
        if obj.is_active:
            return self.html.badge("Active", variant="success", icon=Icons.CHECK_CIRCLE)
        else:
            return self.html.badge("Inactive", variant="secondary", icon=Icons.PAUSE_CIRCLE)

    @computed_field("Usage")
    def usage_count_display(self, obj: ToolsetConfiguration) -> str:
        """Usage count display."""
        if not obj.usage_count:
            return "Not used"
        return f"{obj.usage_count} times"

    @computed_field("Created By")
    def created_by_display(self, obj: ToolsetConfiguration) -> str:
        """Created by user display."""
        if not obj.created_by:
            return "—"
        # Simple username display, UserField handles avatar and styling
        return obj.created_by.username

    @computed_field("Created")
    def created_at_display(self, obj: ToolsetConfiguration) -> str:
        """Created time with relative display."""
        # DateTimeField in display_fields handles formatting automatically
        return obj.created_at

    # Old-style actions (TODO: Migrate to new ActionConfig system when available)
    def activate_configurations(self, request, queryset):
        """Activate selected configurations."""
        updated = queryset.update(is_active=True)
        messages.success(request, f"Activated {updated} configurations.")
    activate_configurations.short_description = "Activate configurations"

    def deactivate_configurations(self, request, queryset):
        """Deactivate selected configurations."""
        updated = queryset.update(is_active=False)
        messages.warning(request, f"Deactivated {updated} configurations.")
    deactivate_configurations.short_description = "Deactivate configurations"

    def reset_usage(self, request, queryset):
        """Reset usage count for selected configurations."""
        updated = queryset.update(usage_count=0)
        messages.info(request, f"Reset usage count for {updated} configurations.")
    reset_usage.short_description = "Reset usage count"
