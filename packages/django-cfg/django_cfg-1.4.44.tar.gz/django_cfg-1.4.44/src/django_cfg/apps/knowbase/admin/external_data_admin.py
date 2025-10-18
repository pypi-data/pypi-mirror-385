"""
External Data Admin v2.0 - NEW Declarative Pydantic Approach

Enhanced external data management with Material Icons and clean declarative config.
"""

from django.contrib import admin, messages
from django.db import models
from django.db.models import Count, Q, Sum
from django.db.models.fields.json import JSONField
from django_json_widget.widgets import JSONEditorWidget
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import AutocompleteSelectFilter
from unfold.contrib.forms.widgets import WysiwygWidget

from django_cfg import ExportMixin
from django_cfg.modules.django_admin import (
    AdminConfig,
    FieldConfig,
    FieldsetConfig,
    Icons,
    computed_field,
)
from django_cfg.modules.django_admin.base import PydanticAdmin
from django_cfg.modules.django_admin.models import StatusBadgeConfig, DateTimeDisplayConfig, MoneyDisplayConfig
from django_cfg.modules.django_admin.utils.badges import StatusBadge
from django_cfg.modules.django_admin.utils.displays import DateTimeDisplay, MoneyDisplay

from ..models.external_data import (
    ExternalData,
    ExternalDataChunk,
)


class ExternalDataChunkInline(TabularInline):
    """Inline for external data chunks with Unfold styling."""

    model = ExternalDataChunk
    verbose_name = "External Data Chunk"
    verbose_name_plural = "🔗 External Data Chunks (Read-only)"
    extra = 0
    max_num = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    fields = [
        'short_uuid', 'chunk_index', 'content_preview_inline', 'token_count',
        'has_embedding_inline', 'embedding_cost'
    ]
    readonly_fields = [
        'short_uuid', 'chunk_index', 'content_preview_inline', 'token_count', 'character_count',
        'has_embedding_inline', 'embedding_cost', 'created_at'
    ]

    hide_title = False
    classes = ['collapse']

    @computed_field("Content Preview")
    def content_preview_inline(self, obj):
        """Shortened content preview for inline display."""
        if not obj.content:
            return "—"
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content

    @computed_field("Has Embedding")
    def has_embedding_inline(self, obj):
        """Check if chunk has embedding vector for inline."""
        return obj.embedding is not None and len(obj.embedding) > 0

    def get_queryset(self, request):
        """Optimize queryset for inline display."""
        return super().get_queryset(request).select_related('external_data', 'user')


# ===== External Data Admin Config =====

external_data_config = AdminConfig(
    model=ExternalData,

    # Performance optimization
    select_related=['user', 'category'],

    # List display
    list_display=[
        "title_display",
        "source_type_display",
        "source_identifier_display",
        "user_display",
        "status_display",
        "chunks_count_display",
        "tokens_display",
        "cost_display",
        "visibility_display",
        "processed_at_display",
        "created_at_display"
    ],

    # Search and filters
    search_fields=["title", "description", "source_identifier", "user__username", "user__email"],
    list_filter=["source_type", "status", "is_active", "is_public", "embedding_model", "processed_at", "created_at"],

    # Ordering
    ordering=["-created_at"],
)


@admin.register(ExternalData)
class ExternalDataAdmin(PydanticAdmin):
    """
    External Data admin using NEW Pydantic declarative approach.

    Features:
    - Declarative configuration with type safety
    - Automatic display method generation
    - Material Icons integration
    - Custom actions for data processing
    - Statistics in changelist_view
    - Chunk management via inline

    Note: Actions use old-style decorators as ActionConfig is not yet available in v2.0
    """
    config = external_data_config

    # Override list_display_links
    list_display_links = ["title_display"]

    # Override list_filter to add custom filters
    list_filter = [
        "source_type", "status", "is_active", "is_public",
        "embedding_model", "processed_at", "created_at",
        ("user", AutocompleteSelectFilter),
        ("category", AutocompleteSelectFilter)
    ]

    # Inlines
    inlines = [ExternalDataChunkInline]

    # Autocomplete
    autocomplete_fields = ["user", "category"]

    # Readonly fields
    readonly_fields = [
        "id", "user", "source_type", "source_identifier", "status",
        "processed_at", "processing_error",
        "total_chunks", "total_tokens", "processing_cost",
        "created_at", "updated_at"
    ]

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="External Data Info",
            fields=["id", "title", "description", "user", "category"]
        ),
        FieldsetConfig(
            title="Source Details",
            fields=["source_type", "source_identifier", "source_metadata"]
        ),
        FieldsetConfig(
            title="Processing Status",
            fields=["status", "processed_at", "processing_error"]
        ),
        FieldsetConfig(
            title="Statistics",
            fields=["total_chunks", "total_tokens", "processing_cost"]
        ),
        FieldsetConfig(
            title="Settings",
            fields=["is_active", "is_public", "embedding_model"]
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at"],
            collapsed=True
        )
    ]

    # Unfold configuration
    compressed_fields = True
    warn_unsaved_form = True

    # Form field overrides
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget}
    }

    # Actions
    actions = ['reprocess_data', 'activate_data', 'deactivate_data', 'mark_as_public', 'mark_as_private']

    # Custom display methods using @computed_field decorator
    @computed_field("Title")
    def title_display(self, obj: ExternalData) -> str:
        """Display external data title."""
        title = obj.title or "Untitled External Data"
        if len(title) > 50:
            title = title[:47] + "..."

        config = StatusBadgeConfig(show_icons=True, icon=Icons.CLOUD)
        return StatusBadge.create(
            text=title,
            variant="primary",
            config=config
        )

    @computed_field("Source Type")
    def source_type_display(self, obj: ExternalData) -> str:
        """Display source type with badge."""
        if not obj.source_type:
            return "—"

        type_variants = {
            'api': 'info',
            'webhook': 'success',
            'database': 'warning',
            'file': 'secondary'
        }
        variant = type_variants.get(obj.source_type.lower(), 'secondary')

        type_icons = {
            'api': Icons.API,
            'webhook': Icons.WEBHOOK,
            'database': Icons.STORAGE,
            'file': Icons.INSERT_DRIVE_FILE
        }
        icon = type_icons.get(obj.source_type.lower(), Icons.CLOUD)

        config = StatusBadgeConfig(show_icons=True, icon=icon)
        return StatusBadge.create(
            text=obj.source_type.upper(),
            variant=variant,
            config=config
        )

    @computed_field("Source ID")
    def source_identifier_display(self, obj: ExternalData) -> str:
        """Display source identifier with truncation."""
        if not obj.source_identifier:
            return "—"

        identifier = obj.source_identifier
        if len(identifier) > 30:
            identifier = identifier[:27] + "..."

        return identifier

    @computed_field("User")
    def user_display(self, obj: ExternalData) -> str:
        """User display."""
        if not obj.user:
            return "—"
        from django_cfg.modules.django_admin.utils.displays import UserDisplay
        return UserDisplay.simple(obj.user)

    @computed_field("Status")
    def status_display(self, obj: ExternalData) -> str:
        """Display processing status."""
        icon_map = {
            'pending': Icons.SCHEDULE,
            'processing': Icons.SCHEDULE,
            'completed': Icons.CHECK_CIRCLE,
            'failed': Icons.ERROR,
            'cancelled': Icons.CANCEL
        }

        variant_map = {
            'pending': 'warning',
            'processing': 'info',
            'completed': 'success',
            'failed': 'danger',
            'cancelled': 'secondary'
        }

        icon = icon_map.get(obj.status, Icons.SCHEDULE)
        variant = variant_map.get(obj.status, 'warning')

        config = StatusBadgeConfig(show_icons=True, icon=icon)
        return StatusBadge.create(
            text=obj.get_status_display() if hasattr(obj, 'get_status_display') else obj.status.title(),
            variant=variant,
            config=config
        )

    @computed_field("Chunks")
    def chunks_count_display(self, obj: ExternalData) -> str:
        """Display chunks count."""
        count = obj.total_chunks or 0
        return f"{count} chunks"

    @computed_field("Tokens")
    def tokens_display(self, obj: ExternalData) -> str:
        """Display token count with formatting."""
        tokens = obj.total_tokens or 0
        if tokens > 1000:
            return f"{tokens/1000:.1f}K"
        return str(tokens)

    @computed_field("Cost (USD)")
    def cost_display(self, obj: ExternalData) -> str:
        """Display cost with currency formatting."""
        config = MoneyDisplayConfig(
            currency="USD",
            decimal_places=6,
            show_sign=False
        )
        return MoneyDisplay.format_amount(obj.processing_cost or 0, config)

    @computed_field("Visibility")
    def visibility_display(self, obj: ExternalData) -> str:
        """Display visibility status."""
        if obj.is_public:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.PUBLIC)
            return StatusBadge.create(text="Public", variant="success", config=config)
        else:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.LOCK)
            return StatusBadge.create(text="Private", variant="danger", config=config)

    @computed_field("Processed")
    def processed_at_display(self, obj: ExternalData) -> str:
        """Processed time with relative display."""
        if not obj.processed_at:
            return "—"
        config = DateTimeDisplayConfig(show_relative=True)
        return DateTimeDisplay.relative(obj.processed_at, config)

    @computed_field("Created")
    def created_at_display(self, obj: ExternalData) -> str:
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return DateTimeDisplay.relative(obj.created_at, config)

    # Old-style actions (TODO: Migrate to new ActionConfig system when available)
    def reprocess_data(self, request, queryset):
        """Reprocess selected external data."""
        count = queryset.count()
        messages.info(request, f"Reprocess functionality not implemented yet. {count} items selected.")
    reprocess_data.short_description = "Reprocess data"

    def activate_data(self, request, queryset):
        """Activate selected external data."""
        updated = queryset.update(is_active=True)
        messages.success(request, f"Activated {updated} external data items.")
    activate_data.short_description = "Activate data"

    def deactivate_data(self, request, queryset):
        """Deactivate selected external data."""
        updated = queryset.update(is_active=False)
        messages.warning(request, f"Deactivated {updated} external data items.")
    deactivate_data.short_description = "Deactivate data"

    def mark_as_public(self, request, queryset):
        """Mark selected data as public."""
        updated = queryset.update(is_public=True)
        messages.success(request, f"Marked {updated} items as public.")
    mark_as_public.short_description = "Mark as public"

    def mark_as_private(self, request, queryset):
        """Mark selected data as private."""
        updated = queryset.update(is_public=False)
        messages.warning(request, f"Marked {updated} items as private.")
    mark_as_private.short_description = "Mark as private"

    def changelist_view(self, request, extra_context=None):
        """Add external data statistics to changelist."""
        extra_context = extra_context or {}

        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_items=Count('id'),
            active_items=Count('id', filter=Q(is_active=True)),
            completed_items=Count('id', filter=Q(status='completed')),
            total_chunks=Sum('total_chunks'),
            total_tokens=Sum('total_tokens'),
            total_cost=Sum('processing_cost')
        )

        # Source type breakdown
        source_type_counts = dict(
            queryset.values_list('source_type').annotate(
                count=Count('id')
            )
        )

        extra_context['external_data_stats'] = {
            'total_items': stats['total_items'] or 0,
            'active_items': stats['active_items'] or 0,
            'completed_items': stats['completed_items'] or 0,
            'total_chunks': stats['total_chunks'] or 0,
            'total_tokens': stats['total_tokens'] or 0,
            'total_cost': f"${(stats['total_cost'] or 0):.6f}",
            'source_type_counts': source_type_counts
        }

        return super().changelist_view(request, extra_context)


# ===== External Data Chunk Admin Config =====

external_data_chunk_config = AdminConfig(
    model=ExternalDataChunk,

    # Performance optimization
    select_related=['external_data', 'user'],

    # List display
    list_display=[
        "chunk_display",
        "external_data_display",
        "user_display",
        "token_count_display",
        "embedding_status",
        "embedding_cost_display",
        "created_at_display"
    ],

    # Search and filters
    search_fields=["external_data__title", "user__username", "content"],
    list_filter=["embedding_model", "created_at"],

    # Ordering
    ordering=["-created_at"],
)


@admin.register(ExternalDataChunk)
class ExternalDataChunkAdmin(PydanticAdmin):
    """
    External Data Chunk admin using NEW Pydantic declarative approach.

    Features:
    - Declarative configuration with type safety
    - Automatic display method generation
    - Material Icons integration
    - Custom actions for embedding management
    - Embedding status visualization

    Note: Actions use old-style decorators as ActionConfig is not yet available in v2.0
    """
    config = external_data_chunk_config

    # Override list_display_links
    list_display_links = ["chunk_display"]

    # Override list_filter to add custom filters
    list_filter = [
        "embedding_model", "created_at",
        ("user", AutocompleteSelectFilter),
        ("external_data", AutocompleteSelectFilter)
    ]

    # Autocomplete
    autocomplete_fields = ["external_data", "user"]

    # Readonly fields
    readonly_fields = [
        "id", "token_count", "character_count", "embedding_cost",
        "created_at", "updated_at", "content_preview"
    ]

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="Chunk Info",
            fields=["id", "external_data", "user", "chunk_index"]
        ),
        FieldsetConfig(
            title="Content",
            fields=["content_preview", "content"]
        ),
        FieldsetConfig(
            title="Embedding",
            fields=["embedding_model", "token_count", "character_count", "embedding_cost"]
        ),
        FieldsetConfig(
            title="Vector",
            fields=["embedding"],
            collapsed=True
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at"],
            collapsed=True
        )
    ]

    # Actions
    actions = ['regenerate_embeddings', 'clear_embeddings']

    # Custom display methods using @computed_field decorator
    @computed_field("Chunk")
    def chunk_display(self, obj: ExternalDataChunk) -> str:
        """Display chunk identifier."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.ARTICLE)
        return StatusBadge.create(
            text=f"Chunk {obj.chunk_index + 1}",
            variant="info",
            config=config
        )

    @computed_field("External Data")
    def external_data_display(self, obj: ExternalDataChunk) -> str:
        """Display external data title."""
        return obj.external_data.title or "Untitled External Data"

    @computed_field("User")
    def user_display(self, obj: ExternalDataChunk) -> str:
        """User display."""
        if not obj.user:
            return "—"
        from django_cfg.modules.django_admin.utils.displays import UserDisplay
        return UserDisplay.simple(obj.user)

    @computed_field("Tokens")
    def token_count_display(self, obj: ExternalDataChunk) -> str:
        """Display token count with formatting."""
        tokens = obj.token_count
        if tokens > 1000:
            return f"{tokens/1000:.1f}K"
        return str(tokens)

    @computed_field("Embedding")
    def embedding_status(self, obj: ExternalDataChunk) -> str:
        """Display embedding status."""
        has_embedding = obj.embedding is not None and len(obj.embedding) > 0
        if has_embedding:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.CHECK_CIRCLE)
            return StatusBadge.create(text="✓ Vectorized", variant="success", config=config)
        else:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.ERROR)
            return StatusBadge.create(text="✗ Not vectorized", variant="danger", config=config)

    @computed_field("Cost (USD)")
    def embedding_cost_display(self, obj: ExternalDataChunk) -> str:
        """Display embedding cost with currency formatting."""
        config = MoneyDisplayConfig(
            currency="USD",
            decimal_places=6,
            show_sign=False
        )
        return MoneyDisplay.format_amount(obj.embedding_cost or 0, config)

    @computed_field("Created")
    def created_at_display(self, obj: ExternalDataChunk) -> str:
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return DateTimeDisplay.relative(obj.created_at, config)

    @computed_field("Content Preview")
    def content_preview(self, obj: ExternalDataChunk) -> str:
        """Display content preview with truncation."""
        return obj.content[:200] + "..." if len(obj.content) > 200 else obj.content

    # Old-style actions (TODO: Migrate to new ActionConfig system when available)
    def regenerate_embeddings(self, request, queryset):
        """Regenerate embeddings for selected chunks."""
        count = queryset.count()
        messages.info(request, f"Regenerate embeddings functionality not implemented yet. {count} chunks selected.")
    regenerate_embeddings.short_description = "Regenerate embeddings"

    def clear_embeddings(self, request, queryset):
        """Clear embeddings for selected chunks."""
        updated = queryset.update(embedding=None)
        messages.warning(request, f"Cleared embeddings for {updated} chunks.")
    clear_embeddings.short_description = "Clear embeddings"
