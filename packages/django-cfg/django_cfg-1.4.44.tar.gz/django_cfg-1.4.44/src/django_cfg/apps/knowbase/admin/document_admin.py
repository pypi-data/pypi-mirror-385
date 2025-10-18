"""
Document admin interfaces using NEW Django Admin v2.0.

Enhanced document management with Material Icons and clean declarative config.
"""

from django.contrib import admin, messages
from django.db import IntegrityError, models
from django.db.models.fields.json import JSONField
from django_json_widget.widgets import JSONEditorWidget
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import AutocompleteSelectFilter, AutocompleteSelectMultipleFilter
from unfold.contrib.forms.widgets import WysiwygWidget

from django_cfg import ExportForm, ImportForm
from django_cfg.modules.django_admin import (
    AdminConfig,
    FieldConfig,
    FieldsetConfig,
    Icons,
    computed_field,
)
from django_cfg.modules.django_admin.base import PydanticAdmin
from django_cfg.modules.django_admin.models import StatusBadgeConfig, DateTimeDisplayConfig
from django_cfg.modules.django_admin.utils.badges import StatusBadge
from django_cfg.modules.django_admin.utils.displays import UserDisplay, DateTimeDisplay

from ..models import Document, DocumentCategory, DocumentChunk
from .actions.visibility_actions import mark_as_private, mark_as_public
from .helpers import (
    CategoryStatistics,
    ChunkStatistics,
    DocumentAdminConfigs,
    DocumentStatistics,
)


class DocumentChunkInline(TabularInline):
    """Inline for document chunks with Unfold styling."""

    model = DocumentChunk
    verbose_name = "Document Chunk"
    verbose_name_plural = "📄 Document Chunks (Read-only)"
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
        content = obj.content
        if len(content) > 100:
            return content[:100] + "..."
        return content

    @computed_field("Has Embedding")
    def has_embedding_inline(self, obj):
        """Check if chunk has embedding vector for inline."""
        return obj.embedding is not None and len(obj.embedding) > 0

    def get_queryset(self, request):
        """Optimize queryset for inline display."""
        return super().get_queryset(request).select_related('document', 'user')


# ===== Document Admin Config =====

document_config = AdminConfig(
    model=Document,

    # Performance optimization
    select_related=['user'],
    prefetch_related=['categories'],

    # Import/Export
    import_export_enabled=True,

    # List display
    list_display=[
        'title_display',
        'categories_display',
        'user_display',
        'visibility_display',
        'status_display',
        'chunks_count_display',
        'vectorization_progress',
        'tokens_display',
        'cost_display',
        'created_at_display'
    ],

    # Search and filters
    search_fields=['title', 'user__username', 'user__email'],
    list_filter=['processing_status', 'is_public', 'file_type', 'created_at'],

    # Ordering
    ordering=['-created_at'],
)


@admin.register(Document)
class DocumentAdmin(PydanticAdmin):
    """
    Document admin using NEW Pydantic declarative approach.

    Features:
    - Declarative configuration with type safety
    - Automatic display method generation
    - Material Icons integration
    - Import/Export functionality (via config)
    - Custom actions for document processing
    - Statistics in changelist_view
    """
    config = document_config

    # Override list_display_links
    list_display_links = ['title_display']

    # Override list_filter to add custom filters
    list_filter = [
        'processing_status', 'is_public', 'file_type', 'created_at',
        ('user', AutocompleteSelectFilter),
        ('categories', AutocompleteSelectMultipleFilter)
    ]

    # Autocomplete
    autocomplete_fields = ['user', 'categories']

    # Readonly fields
    readonly_fields = [
        'id', 'user', 'content_hash', 'file_size', 'processing_started_at',
        'processing_completed_at', 'chunks_count', 'total_tokens',
        'processing_error', 'processing_duration', 'processing_status',
        'total_cost_usd', 'created_at', 'updated_at', 'duplicate_check'
    ]

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="Basic Information",
            fields=["id", "title", "user", "categories", "is_public", "file_type", "file_size"]
        ),
        FieldsetConfig(
            title="Content",
            fields=["content", "content_hash", "duplicate_check"]
        ),
        FieldsetConfig(
            title="Processing Status",
            fields=['processing_status', 'processing_started_at', 'processing_completed_at', 'processing_error']
        ),
        FieldsetConfig(
            title="Statistics",
            fields=["chunks_count", "total_tokens", "total_cost_usd"]
        ),
        FieldsetConfig(
            title="Metadata",
            fields=["metadata"],
            collapsed=True
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at"],
            collapsed=True
        )
    ]

    # Inline
    inlines = [DocumentChunkInline]

    # Filter horizontal
    filter_horizontal = ['categories']

    # Unfold configuration
    compressed_fields = True
    warn_unsaved_form = True

    # Form field overrides
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget}
    }

    # Actions
    actions = ['reprocess_documents', 'mark_as_public', 'mark_as_private']

    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related."""
        queryset = Document.objects.all_users().select_related('user').prefetch_related('categories')

        # Staff users see all documents, regular users see only their own
        if not request.user.is_staff:
            queryset = queryset.filter(user=request.user)

        return queryset

    def save_model(self, request, obj, form, change):
        """Automatically set user to current user when creating new documents."""
        if not change:
            obj.user = request.user

            is_duplicate, existing_doc = Document.objects.check_duplicate_before_save(
                user=obj.user,
                content=obj.content
            )

            if is_duplicate and existing_doc:
                messages.error(
                    request,
                    f'A document with identical content already exists: "{existing_doc.title}" '
                    f'(created {existing_doc.created_at.strftime("%Y-%m-%d %H:%M")}). '
                    f'Please modify the content or update the existing document.'
                )
                return

        try:
            super().save_model(request, obj, form, change)
        except IntegrityError as e:
            if 'unique_user_document' in str(e):
                messages.error(
                    request,
                    'A document with identical content already exists for this user. '
                    'Please modify the content or update the existing document.'
                )
            else:
                messages.error(request, f'Database error: {str(e)}')
            raise

    # Custom display methods using @computed_field decorator
    @computed_field("Document Title")
    def title_display(self, obj: Document) -> str:
        """Display document title with truncation."""
        title = obj.title or "Untitled Document"
        if len(title) > 50:
            title = title[:47] + "..."

        return StatusBadge.create(
            text=title,
            variant="primary",
            config=DocumentAdminConfigs.DOCUMENT_TITLE
        )

    @computed_field("Categories")
    def categories_display(self, obj: Document) -> str:
        """Display categories count."""
        categories = obj.categories.all()

        if not categories:
            return "No categories"

        public_count = sum(1 for cat in categories if cat.is_public)
        private_count = len(categories) - public_count

        if private_count == 0:
            return f"{len(categories)} public"
        elif public_count == 0:
            return f"{len(categories)} private"
        else:
            return f"{public_count} public, {private_count} private"

    @computed_field("Assigned User")
    def user_display(self, obj: Document) -> str:
        """Display user."""
        if not obj.user:
            return "—"
        return UserDisplay.simple(obj.user)

    @computed_field("Visibility")
    def visibility_display(self, obj: Document) -> str:
        """Display visibility status."""
        if obj.is_public:
            return StatusBadge.create(text="Public", variant="success")
        return StatusBadge.create(text="Private", variant="danger")

    @computed_field("Status")
    def status_display(self, obj: Document) -> str:
        """Display processing status."""
        icon = DocumentAdminConfigs.get_processing_status_icon(obj.processing_status)

        status_map = {
            'pending': 'info',
            'processing': 'warning',
            'completed': 'success',
            'failed': 'danger'
        }
        variant = status_map.get(obj.processing_status, 'info')

        config = StatusBadgeConfig(show_icons=True, icon=icon)
        return StatusBadge.create(
            text=obj.get_processing_status_display(),
            variant=variant,
            config=config
        )

    @computed_field("Chunks")
    def chunks_count_display(self, obj: Document) -> str:
        """Display chunks count."""
        count = obj.chunks_count
        if count > 0:
            return f"{count} chunks"
        return "0 chunks"

    @computed_field("Vectorization")
    def vectorization_progress(self, obj: Document) -> str:
        """Display vectorization progress."""
        return Document.objects.get_vectorization_status_display(obj)

    @computed_field("Tokens")
    def tokens_display(self, obj: Document) -> str:
        """Display token count."""
        tokens = obj.total_tokens or 0
        if tokens > 1000:
            return f"{tokens/1000:.1f}K"
        return str(tokens)

    @computed_field("Cost")
    def cost_display(self, obj: Document) -> str:
        """Display cost in USD."""
        if not hasattr(obj, 'total_cost_usd') or obj.total_cost_usd is None:
            return "—"
        return f"${obj.total_cost_usd:.4f}"

    @computed_field("Created")
    def created_at_display(self, obj: Document) -> str:
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return DateTimeDisplay.relative(obj.created_at, config)

    @computed_field("Processing Duration")
    def processing_duration_display(self, obj: Document) -> str:
        """Display processing duration in readable format."""
        duration = obj.processing_duration
        if duration is None:
            return "N/A"

        if duration < 60:
            return f"{duration:.1f}s"
        elif duration < 3600:
            minutes = duration / 60
            return f"{minutes:.1f}m"
        else:
            hours = duration / 3600
            return f"{hours:.1f}h"

    @computed_field("Duplicate Check")
    def duplicate_check(self, obj: Document) -> str:
        """Check for duplicate documents with same content."""
        duplicate_info = Document.objects.get_duplicate_info(obj)

        if isinstance(duplicate_info, str):
            if "No duplicates found" in duplicate_info:
                return "No duplicates found"
            return duplicate_info

        duplicates_data = duplicate_info['duplicates']
        count = duplicate_info['count']

        duplicate_names = [dup.title for dup in duplicates_data[:3]]
        result = f"Found {count} duplicate(s): " + ", ".join(duplicate_names)
        if count > 3:
            result += f" and {count - 3} more"

        return result

    # Actions (old-style)
    def reprocess_documents(self, request, queryset):
        """Reprocess selected documents."""
        count = queryset.count()
        messages.info(request, f"Reprocessing functionality not implemented yet. {count} documents selected.")
    reprocess_documents.short_description = "Reprocess documents"

    # Visibility actions
    mark_as_public = mark_as_public
    mark_as_private = mark_as_private

    def changelist_view(self, request, extra_context=None):
        """Add summary statistics to changelist."""
        extra_context = extra_context or {}
        queryset = self.get_queryset(request)
        extra_context['summary_stats'] = DocumentStatistics.get_document_stats(queryset)
        return super().changelist_view(request, extra_context)


# ===== Document Chunk Admin Config =====

chunk_config = AdminConfig(
    model=DocumentChunk,

    # Performance optimization
    select_related=['document', 'user'],

    # List display
    list_display=[
        'chunk_display',
        'document_display',
        'user_display',
        'token_count_display',
        'embedding_status',
        'embedding_cost_display',
        'created_at_display'
    ],

    # Search and filters
    search_fields=['document__title', 'user__username', 'content'],
    list_filter=['embedding_model', 'created_at'],

    # Ordering
    ordering=['-created_at'],
)


@admin.register(DocumentChunk)
class DocumentChunkAdmin(PydanticAdmin):
    """
    Document Chunk admin using NEW Pydantic declarative approach.

    Features:
    - Declarative configuration with type safety
    - Automatic display method generation
    - Material Icons integration
    - Custom actions for embedding management
    - Statistics in changelist_view
    """
    config = chunk_config

    # Override list_display_links
    list_display_links = ['chunk_display']

    # Override list_filter to add custom filters
    list_filter = [
        'embedding_model', 'created_at',
        ('user', AutocompleteSelectFilter),
        ('document', AutocompleteSelectFilter)
    ]

    # Readonly fields
    readonly_fields = [
        'id', 'embedding_info', 'token_count', 'character_count',
        'embedding_cost', 'created_at', 'updated_at', 'content_preview'
    ]

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="Basic Information",
            fields=["id", "document", "user", "chunk_index"]
        ),
        FieldsetConfig(
            title="Content",
            fields=["content_preview", "content"]
        ),
        FieldsetConfig(
            title="Embedding Information",
            fields=["embedding_model", "token_count", "character_count", "embedding_cost"]
        ),
        FieldsetConfig(
            title="Vector Embedding",
            fields=["embedding"],
            collapsed=True
        ),
        FieldsetConfig(
            title="Metadata",
            fields=["metadata"],
            collapsed=True
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
        JSONField: {"widget": JSONEditorWidget}
    }

    # Actions
    actions = ['regenerate_embeddings', 'clear_embeddings']

    # Custom display methods using @computed_field decorator
    @computed_field("Chunk")
    def chunk_display(self, obj: DocumentChunk) -> str:
        """Display chunk identifier."""
        return StatusBadge.create(
            text=f"Chunk {obj.chunk_index + 1}",
            variant="info",
            config=DocumentAdminConfigs.CHUNK
        )

    @computed_field("Document")
    def document_display(self, obj: DocumentChunk) -> str:
        """Display document title."""
        return obj.document.title

    @computed_field("Assigned User")
    def user_display(self, obj: DocumentChunk) -> str:
        """Display user."""
        if not obj.user:
            return "—"
        return UserDisplay.simple(obj.user)

    @computed_field("Tokens")
    def token_count_display(self, obj: DocumentChunk) -> str:
        """Display token count."""
        tokens = obj.token_count or 0
        if tokens > 1000:
            return f"{tokens/1000:.1f}K"
        return str(tokens)

    @computed_field("Embedding Status")
    def embedding_status(self, obj: DocumentChunk) -> str:
        """Display embedding status."""
        has_embedding = obj.embedding is not None and len(obj.embedding) > 0
        if has_embedding:
            return StatusBadge.create(text="✓ Vectorized", variant="success")
        return StatusBadge.create(text="✗ Not vectorized", variant="danger")

    @computed_field("Embedding Cost")
    def embedding_cost_display(self, obj: DocumentChunk) -> str:
        """Display embedding cost."""
        if not hasattr(obj, 'embedding_cost') or obj.embedding_cost is None:
            return "—"
        return f"${obj.embedding_cost:.6f}"

    @computed_field("Created")
    def created_at_display(self, obj: DocumentChunk) -> str:
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return DateTimeDisplay.relative(obj.created_at, config)

    @computed_field("Content Preview")
    def content_preview(self, obj: DocumentChunk) -> str:
        """Display content preview."""
        if not obj.content:
            return "—"
        content = obj.content
        if len(content) > 200:
            return content[:200] + "..."
        return content

    @computed_field("Embedding Info")
    def embedding_info(self, obj: DocumentChunk) -> str:
        """Display embedding information safely."""
        if obj.embedding is not None and len(obj.embedding) > 0:
            return f"Vector ({len(obj.embedding)} dimensions)"
        return "No embedding"

    # Actions (old-style)
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

    def changelist_view(self, request, extra_context=None):
        """Add chunk statistics to changelist."""
        extra_context = extra_context or {}
        queryset = self.get_queryset(request)
        extra_context['chunk_stats'] = ChunkStatistics.get_chunk_stats(queryset)
        return super().changelist_view(request, extra_context)


# ===== Document Category Admin Config =====

category_config = AdminConfig(
    model=DocumentCategory,

    # Performance optimization
    prefetch_related=['documents'],

    # Import/Export
    import_export_enabled=True,

    # List display
    list_display=[
        'short_uuid',
        'name_display',
        'visibility_display',
        'document_count',
        'created_at_display'
    ],

    # Search and filters
    search_fields=['name', 'description'],
    list_filter=['is_public', 'created_at'],

    # Ordering
    ordering=['-created_at'],
)


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(PydanticAdmin):
    """
    Document Category admin using NEW Pydantic declarative approach.

    Features:
    - Declarative configuration with type safety
    - Automatic display method generation
    - Material Icons integration
    - Import/Export functionality (via config)
    - Custom actions for visibility management
    - Statistics in changelist_view
    """
    config = category_config

    # Override list_display_links
    list_display_links = ['name_display']

    # Readonly fields
    readonly_fields = ['id', 'created_at', 'updated_at']

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="Basic Information",
            fields=["id", "name", "description", "is_public"]
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
        models.TextField: {"widget": WysiwygWidget}
    }

    # Actions
    actions = ['make_public', 'make_private']

    # Custom display methods using @computed_field decorator
    @computed_field("Category Name")
    def name_display(self, obj: DocumentCategory) -> str:
        """Display category name."""
        return StatusBadge.create(
            text=obj.name,
            variant="primary",
            config=DocumentAdminConfigs.CATEGORY
        )

    @computed_field("Visibility")
    def visibility_display(self, obj: DocumentCategory) -> str:
        """Display visibility status."""
        if obj.is_public:
            return StatusBadge.create(text="Public", variant="success")
        return StatusBadge.create(text="Private", variant="danger")

    @computed_field("Documents")
    def document_count(self, obj: DocumentCategory) -> str:
        """Display count of documents in this category."""
        count = obj.documents.count()
        return f"{count} documents"

    @computed_field("Created")
    def created_at_display(self, obj: DocumentCategory) -> str:
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return DateTimeDisplay.relative(obj.created_at, config)

    # Visibility actions
    make_public = mark_as_public
    make_private = mark_as_private

    def get_queryset(self, request):
        """Optimize queryset with prefetch_related."""
        return super().get_queryset(request).prefetch_related('documents')

    def changelist_view(self, request, extra_context=None):
        """Add category statistics to changelist."""
        extra_context = extra_context or {}
        queryset = self.get_queryset(request)
        extra_context['category_stats'] = CategoryStatistics.get_category_stats(queryset)
        return super().changelist_view(request, extra_context)
