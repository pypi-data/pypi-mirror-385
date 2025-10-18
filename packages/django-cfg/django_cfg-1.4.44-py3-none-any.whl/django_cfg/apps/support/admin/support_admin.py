"""
Support Admin v2.0 - NEW Declarative Pydantic Approach

Enhanced support ticket management with Material Icons and auto-generated displays.
"""

from django.contrib import admin
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import TabularInline

from django_cfg.modules.django_admin import (
    ActionConfig,
    AdminConfig,
    FieldConfig,
    FieldsetConfig,
    Icons,
    computed_field,
)
from django_cfg.modules.django_admin.base import PydanticAdmin
from django_cfg.modules.django_admin.models import StatusBadgeConfig
from django_cfg.modules.django_admin.utils.badges import StatusBadge

from ..models import Message, Ticket
from .filters import MessageSenderEmailFilter, TicketUserEmailFilter, TicketUserNameFilter
from .resources import MessageResource, TicketResource


class MessageInline(TabularInline):
    """Read-only inline for viewing messages. Use Chat interface for replies."""

    model = Message
    extra = 0
    fields = ["sender_display", "created_at", "text_preview"]
    readonly_fields = ["sender_display", "created_at", "text_preview"]
    show_change_link = False
    classes = ('collapse',)

    def has_add_permission(self, request, obj=None):
        """Disable adding messages through admin - use chat interface instead."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable deleting messages through admin."""
        return False

    @computed_field("Sender")
    def sender_display(self, obj):
        """Display sender with badge."""
        if not obj.sender:
            return "—"

        # Determine sender type and variant
        if obj.sender.is_superuser:
            variant = "danger"
            icon = Icons.ADMIN_PANEL_SETTINGS
        elif obj.sender.is_staff:
            variant = "primary"
            icon = Icons.SUPPORT_AGENT
        else:
            variant = "info"
            icon = Icons.PERSON

        config = StatusBadgeConfig(show_icons=True, icon=icon)
        return StatusBadge.create(
            text=obj.sender.get_full_name() or obj.sender.username,
            variant=variant,
            config=config
        )

    @computed_field("Message")
    def text_preview(self, obj):
        """Display message preview."""
        if not obj.text:
            return "—"

        preview = obj.text[:100]
        if len(obj.text) > 100:
            preview += "..."

        return preview


# ===== Ticket Admin Config =====

ticket_config = AdminConfig(
    model=Ticket,

    # Performance optimization
    select_related=['user'],

    # Import/Export
    import_export_enabled=True,
    resource_class=TicketResource,

    # List display
    list_display=[
        "user",
        "uuid",
        "subject",
        "status",
        "last_message",
        "last_message_ago",
        "chat_link",
        "created_at"
    ],

    # Display fields with UI widgets (auto-generates display methods)
    display_fields=[
        FieldConfig(
            name="user",
            title="User",
            ui_widget="user_avatar",
            header=True
        ),
        FieldConfig(
            name="uuid",
            title="UUID",
            ui_widget="badge",
            variant="secondary",
            icon=Icons.CONFIRMATION_NUMBER
        ),
        FieldConfig(
            name="subject",
            title="Subject",
            ui_widget="badge",
            variant="primary",
            icon=Icons.SUBJECT
        ),
        FieldConfig(
            name="status",
            title="Status",
            ui_widget="badge",
            label_map={
                'open': 'info',
                'waiting_for_user': 'warning',
                'waiting_for_admin': 'primary',
                'resolved': 'success',
                'closed': 'secondary'
            },
            icon=Icons.NEW_RELEASES
        ),
        FieldConfig(
            name="last_message",
            title="Last Message",
            ui_widget="text"
        ),
        FieldConfig(
            name="last_message_ago",
            title="Last Activity",
            ui_widget="datetime_relative"
        ),
        FieldConfig(
            name="chat_link",
            title="Chat",
            ui_widget="text"
        ),
        FieldConfig(
            name="created_at",
            title="Created",
            ui_widget="datetime_relative",
            ordering="created_at"
        ),
    ],

    # Search and filters
    search_fields=["uuid", "user__username", "user__email", "subject"],
    list_filter=["status", "created_at", TicketUserEmailFilter, TicketUserNameFilter],

    # Readonly fields for change form
    readonly_fields=["uuid", "user", "created_at", "chat_link_detail"],

    # Actions
    actions=[
        ActionConfig(
            name="mark_as_open",
            description="Mark as open",
            variant="info",
            handler="django_cfg.apps.support.admin.actions.mark_tickets_as_open"
        ),
        ActionConfig(
            name="mark_as_waiting_for_user",
            description="Mark as waiting for user",
            variant="warning",
            handler="django_cfg.apps.support.admin.actions.mark_tickets_as_waiting_for_user"
        ),
        ActionConfig(
            name="mark_as_waiting_for_admin",
            description="Mark as waiting for admin",
            variant="primary",
            handler="django_cfg.apps.support.admin.actions.mark_tickets_as_waiting_for_admin"
        ),
        ActionConfig(
            name="mark_as_resolved",
            description="Mark as resolved",
            variant="success",
            handler="django_cfg.apps.support.admin.actions.mark_tickets_as_resolved"
        ),
        ActionConfig(
            name="mark_as_closed",
            description="Mark as closed",
            variant="danger",
            handler="django_cfg.apps.support.admin.actions.mark_tickets_as_closed"
        ),
    ],

    # Ordering
    ordering=["-created_at"],
)


@admin.register(Ticket)
class TicketAdmin(PydanticAdmin):
    """Ticket admin using NEW Pydantic declarative approach."""
    config = ticket_config

    # Inlines
    inlines = [MessageInline]

    # Autocomplete
    autocomplete_fields = ["user"]

    def get_readonly_fields(self, request, obj=None):
        """Different readonly fields for add/change forms."""
        if obj is None:  # Adding new ticket
            return ("uuid", "created_at")
        else:  # Editing existing ticket
            return ("uuid", "user", "created_at", "chat_link_detail")

    def get_fieldsets(self, request, obj=None):
        """Different fieldsets for add/change forms."""
        if obj is None:  # Adding new ticket
            return (
                ('New Ticket', {
                    "fields": ("user", "subject", "status"),
                    "classes": ("tab",)
                }),
            )
        else:  # Editing existing ticket
            return (
                ('Ticket Information', {
                    "fields": (("uuid", "user"), "subject", "status", "created_at"),
                    "classes": ("tab",)
                }),
                ('Chat Interface', {
                    "description": "Use the Chat interface to reply to this ticket.",
                    "fields": ("chat_link_detail",),
                    "classes": ("tab",)
                }),
            )

    # Custom readonly method for detail view
    def chat_link_detail(self, obj: Ticket) -> str:
        """Display clickable chat link button in detail view."""
        chat_url = reverse('cfg_support:ticket-chat', kwargs={'ticket_uuid': obj.uuid})
        return format_html(
            '<a href="{}" target="_blank" '
            'style="background: #0d6efd; color: white; padding: 8px 16px; '
            'border-radius: 6px; text-decoration: none; font-size: 14px; '
            'display: inline-flex; align-items: center; gap: 8px; font-weight: 500;">'
            '<svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">'
            '<path d="M2.678 11.894a1 1 0 0 1 .287.801 10.97 10.97 0 0 1-.398 2c1.395-.323 2.247-.697 2.634-.893a1 1 0 0 1 .71-.074A8.06 8.06 0 0 0 8 14c3.996 0 7-2.807 7-6 0-3.192-3.004-6-7-6S1 4.808 1 8c0 1.468.617 2.83 1.678 3.894zm-.493 3.905a21.682 21.682 0 0 1-.713.129c-.2.032-.352-.176-.273-.362a9.68 9.68 0 0 0 .244-.637l.003-.01c.248-.72.45-1.548.524-2.319C.743 11.37 0 9.76 0 8c0-3.866 3.582-7 8-7s8 3.134 8 7-3.582 7-8 7a9.06 9.06 0 0 1-2.347-.306c-.52.263-1.639.742-3.468 1.105z"/>'
            '</svg>Open Chat</a>',
            chat_url
        )
    chat_link_detail.short_description = "Chat Link"

    def changelist_view(self, request, extra_context=None):
        """Add ticket statistics to changelist."""
        extra_context = extra_context or {}

        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_tickets=Count('uuid'),
            open_tickets=Count('uuid', filter=Q(status='open')),
            waiting_for_user_tickets=Count('uuid', filter=Q(status='waiting_for_user')),
            waiting_for_admin_tickets=Count('uuid', filter=Q(status='waiting_for_admin')),
            resolved_tickets=Count('uuid', filter=Q(status='resolved')),
            closed_tickets=Count('uuid', filter=Q(status='closed'))
        )

        extra_context['ticket_stats'] = {
            'total_tickets': stats['total_tickets'] or 0,
            'open_tickets': stats['open_tickets'] or 0,
            'waiting_for_user_tickets': stats['waiting_for_user_tickets'] or 0,
            'waiting_for_admin_tickets': stats['waiting_for_admin_tickets'] or 0,
            'resolved_tickets': stats['resolved_tickets'] or 0,
            'closed_tickets': stats['closed_tickets'] or 0
        }

        return super().changelist_view(request, extra_context)


# ===== Message Admin Config =====

message_config = AdminConfig(
    model=Message,

    # Performance optimization
    select_related=['ticket', 'sender'],

    # Import/Export
    import_export_enabled=True,
    resource_class=MessageResource,

    # List display
    list_display=[
        "ticket",
        "sender",
        "text",
        "created_at"
    ],

    # Display fields with UI widgets (auto-generates display methods)
    display_fields=[
        FieldConfig(
            name="ticket",
            title="Ticket",
            ui_widget="badge",
            variant="primary",
            icon=Icons.CONFIRMATION_NUMBER
        ),
        FieldConfig(
            name="sender",
            title="Sender",
            ui_widget="badge",
            variant="info",
            icon=Icons.PERSON
        ),
        FieldConfig(
            name="text",
            title="Message",
            ui_widget="text"
        ),
        FieldConfig(
            name="created_at",
            title="Created",
            ui_widget="datetime_relative",
            ordering="created_at"
        ),
    ],

    # Search and filters
    search_fields=["ticket__uuid", "ticket__subject", "sender__username", "sender__email", "text"],
    list_filter=["created_at", "ticket__status", MessageSenderEmailFilter],

    # Readonly fields
    readonly_fields=["ticket", "sender", "created_at"],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title='Message Information',
            fields=['ticket', 'sender', 'text']
        ),
        FieldsetConfig(
            title='Timestamps',
            fields=['created_at'],
            collapsed=True
        )
    ],

    # Ordering
    ordering=["-created_at"],
)


@admin.register(Message)
class MessageAdmin(PydanticAdmin):
    """Message admin using NEW Pydantic declarative approach."""
    config = message_config

    def has_add_permission(self, request):
        """Disable adding messages through admin - use chat interface instead."""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable editing messages through admin."""
        return False

    def changelist_view(self, request, extra_context=None):
        """Add message statistics to changelist."""
        extra_context = extra_context or {}

        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_messages=Count('uuid'),
            staff_messages=Count('uuid', filter=Q(sender__is_staff=True)),
            user_messages=Count('uuid', filter=Q(sender__is_staff=False))
        )

        # Messages by ticket status
        ticket_status_counts = dict(
            queryset.values_list('ticket__status').annotate(
                count=Count('uuid')
            )
        )

        extra_context['message_stats'] = {
            'total_messages': stats['total_messages'] or 0,
            'staff_messages': stats['staff_messages'] or 0,
            'user_messages': stats['user_messages'] or 0,
            'ticket_status_counts': ticket_status_counts
        }

        return super().changelist_view(request, extra_context)
