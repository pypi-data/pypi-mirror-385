"""
Leads Admin v2.0 - NEW Declarative Pydantic Approach

Clean lead management with auto-generated display methods.
"""

from django.contrib import admin
from django.db.models import Count, Q
from unfold.contrib.filters.admin import AutocompleteSelectFilter

from django_cfg.modules.django_admin import (
    ActionConfig,
    AdminConfig,
    FieldConfig,
    FieldsetConfig,
    Icons,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import Lead
from .resources import LeadResource


# ===== Lead Admin Config =====

lead_config = AdminConfig(
    model=Lead,

    # Performance optimization
    select_related=['user'],

    # Import/Export
    import_export_enabled=True,
    resource_class=LeadResource,

    # List display
    list_display=[
        "name",
        "email",
        "company",
        "contact_type",
        "contact_value",
        "subject",
        "status",
        "user",
        "created_at"
    ],

    # Display fields with UI widgets (auto-generates display methods)
    display_fields=[
        FieldConfig(
            name="name",
            title="Name",
            ui_widget="badge",
            variant="primary",
            icon=Icons.PERSON,
            header=True
        ),
        FieldConfig(
            name="email",
            title="Email",
            ui_widget="badge",
            variant="info",
            icon=Icons.EMAIL
        ),
        FieldConfig(
            name="company",
            title="Company",
            ui_widget="badge",
            variant="secondary",
            icon=Icons.BUSINESS,
            empty_value="—"
        ),
        FieldConfig(
            name="contact_type",
            title="Contact Type",
            ui_widget="badge",
            variant="secondary",
            icon=Icons.CONTACT_PHONE,
            label_map={
                "email": "info",
                "phone": "success",
                "telegram": "primary",
                "whatsapp": "success",
                "other": "secondary"
            }
        ),
        FieldConfig(
            name="contact_value",
            title="Contact Value",
            ui_widget="text",
            empty_value="—"
        ),
        FieldConfig(
            name="subject",
            title="Subject",
            ui_widget="text",
            empty_value="—"
        ),
        FieldConfig(
            name="status",
            title="Status",
            ui_widget="badge",
            label_map={
                "new": "info",
                "contacted": "warning",
                "qualified": "primary",
                "converted": "success",
                "rejected": "danger"
            }
        ),
        FieldConfig(
            name="user",
            title="Assigned User",
            ui_widget="user_simple",
            empty_value="—"
        ),
        FieldConfig(
            name="created_at",
            title="Created",
            ui_widget="datetime_relative",
            ordering="created_at"
        ),
    ],

    # Search and filters
    search_fields=["name", "email", "company", "company_site", "message", "subject", "admin_notes"],
    list_filter=["status", "contact_type", "company", "created_at"],

    # Readonly fields
    readonly_fields=["created_at", "updated_at", "ip_address", "user_agent"],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Basic Information",
            fields=["name", "email", "company", "company_site"]
        ),
        FieldsetConfig(
            title="Contact Information",
            fields=["contact_type", "contact_value"]
        ),
        FieldsetConfig(
            title="Message",
            fields=["subject", "message", "extra"]
        ),
        FieldsetConfig(
            title="Metadata",
            fields=["site_url", "ip_address", "user_agent"],
            collapsed=True
        ),
        FieldsetConfig(
            title="Status and Processing",
            fields=["status", "user", "admin_notes"]
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at"],
            collapsed=True
        ),
    ],

    # Actions
    actions=[
        ActionConfig(
            name="mark_as_contacted",
            description="Mark as contacted",
            variant="warning",
            handler="django_cfg.apps.leads.admin.actions.mark_as_contacted"
        ),
        ActionConfig(
            name="mark_as_qualified",
            description="Mark as qualified",
            variant="primary",
            handler="django_cfg.apps.leads.admin.actions.mark_as_qualified"
        ),
        ActionConfig(
            name="mark_as_converted",
            description="Mark as converted",
            variant="success",
            handler="django_cfg.apps.leads.admin.actions.mark_as_converted"
        ),
        ActionConfig(
            name="mark_as_rejected",
            description="Mark as rejected",
            variant="danger",
            handler="django_cfg.apps.leads.admin.actions.mark_as_rejected"
        ),
    ],

    # Ordering
    ordering=["-created_at"],
    list_per_page=50,
    date_hierarchy="created_at",
)


# ===== Lead Admin Class =====

@admin.register(Lead)
class LeadAdmin(PydanticAdmin):
    """
    Lead admin using NEW Pydantic declarative approach.

    Features:
    - Auto-generated display methods from FieldConfig
    - Declarative actions with ActionConfig
    - Import/Export functionality
    - Material Icons integration
    - Clean minimal code
    """
    config = lead_config

    # Override list_filter to add custom filters
    list_filter = ["status", "contact_type", "company", "created_at", ("user", AutocompleteSelectFilter)]

    # Autocomplete
    autocomplete_fields = ["user"]

    # Custom changelist view for statistics
    def changelist_view(self, request, extra_context=None):
        """Add lead statistics to changelist."""
        extra_context = extra_context or {}

        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_leads=Count('id'),
            new_leads=Count('id', filter=Q(status='new')),
            contacted_leads=Count('id', filter=Q(status='contacted')),
            qualified_leads=Count('id', filter=Q(status='qualified')),
            converted_leads=Count('id', filter=Q(status='converted')),
            rejected_leads=Count('id', filter=Q(status='rejected'))
        )

        # Contact type breakdown
        contact_type_counts = dict(
            queryset.values_list('contact_type').annotate(
                count=Count('id')
            )
        )

        # Company breakdown (top 10)
        company_counts = dict(
            queryset.exclude(company__isnull=True).exclude(company='')
            .values_list('company').annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        extra_context['lead_stats'] = {
            'total_leads': stats['total_leads'] or 0,
            'new_leads': stats['new_leads'] or 0,
            'contacted_leads': stats['contacted_leads'] or 0,
            'qualified_leads': stats['qualified_leads'] or 0,
            'converted_leads': stats['converted_leads'] or 0,
            'rejected_leads': stats['rejected_leads'] or 0,
            'contact_type_counts': contact_type_counts,
            'company_counts': company_counts
        }

        return super().changelist_view(request, extra_context)
