"""
Shared admin actions for visibility management.

Provides consistent actions for toggling public/private status across
all knowbase admin interfaces.
"""

from django.contrib import messages


def mark_as_public(modeladmin, request, queryset):
    """Mark selected items as public."""
    updated = queryset.update(is_public=True)
    messages.success(request, f"Marked {updated} item(s) as public.")


def mark_as_private(modeladmin, request, queryset):
    """Mark selected items as private."""
    updated = queryset.update(is_public=False)
    messages.warning(request, f"Marked {updated} item(s) as private.")
