"""
Shared admin actions for knowbase.

Provides reusable actions for admin interfaces.
"""

from .visibility_actions import mark_as_private, mark_as_public

__all__ = [
    'mark_as_public',
    'mark_as_private',
]
