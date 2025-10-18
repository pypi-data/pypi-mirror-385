"""
Widget registry for declarative admin.

Maps ui_widget names to display utilities.
"""

import logging
from typing import Any, Callable, Dict, Optional

from ..models import (
    DateTimeDisplayConfig,
    MoneyDisplayConfig,
    StatusBadgeConfig,
    UserDisplayConfig,
)
from ..utils import (
    CounterBadge,
    DateTimeDisplay,
    MoneyDisplay,
    ProgressBadge,
    StatusBadge,
    UserDisplay,
)

logger = logging.getLogger(__name__)


class WidgetRegistry:
    """
    Widget registry mapping ui_widget names to render functions.

    Maps declarative widget names to actual display utilities.
    """

    _widgets: Dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str, handler: Callable):
        """Register a custom widget."""
        cls._widgets[name] = handler
        logger.debug(f"Registered widget: {name}")

    @classmethod
    def get(cls, name: str) -> Optional[Callable]:
        """Get widget handler by name."""
        return cls._widgets.get(name)

    @classmethod
    def render(cls, widget_name: str, obj: Any, field_name: str, config: Dict[str, Any]):
        """Render field using specified widget."""
        handler = cls.get(widget_name)

        if handler:
            try:
                return handler(obj, field_name, config)
            except Exception as e:
                logger.error(f"Error rendering widget '{widget_name}': {e}")
                return getattr(obj, field_name, "—")

        # Fallback to field value
        logger.warning(f"Widget '{widget_name}' not found, using field value")
        return getattr(obj, field_name, "—")


# Register built-in widgets

# User widgets
WidgetRegistry.register(
    "user_avatar",
    lambda obj, field, cfg: UserDisplay.with_avatar(
        getattr(obj, field),
        UserDisplayConfig(**cfg) if cfg else None
    )
)

WidgetRegistry.register(
    "user_simple",
    lambda obj, field, cfg: UserDisplay.simple(
        getattr(obj, field),
        UserDisplayConfig(**cfg) if cfg else None
    )
)

# Money widgets
WidgetRegistry.register(
    "currency",
    lambda obj, field, cfg: MoneyDisplay.amount(
        getattr(obj, field),
        MoneyDisplayConfig(**cfg) if cfg else None
    )
)

WidgetRegistry.register(
    "money_breakdown",
    lambda obj, field, cfg: MoneyDisplay.with_breakdown(
        getattr(obj, field),
        cfg.get('breakdown_items', []),
        MoneyDisplayConfig(**{k: v for k, v in cfg.items() if k != 'breakdown_items'}) if cfg else None
    )
)

# Badge widgets
WidgetRegistry.register(
    "badge",
    lambda obj, field, cfg: StatusBadge.auto(
        getattr(obj, field),
        StatusBadgeConfig(**cfg) if cfg else None
    )
)

WidgetRegistry.register(
    "progress",
    lambda obj, field, cfg: ProgressBadge.percentage(
        getattr(obj, field)
    )
)

WidgetRegistry.register(
    "counter",
    lambda obj, field, cfg: CounterBadge.simple(
        getattr(obj, field),
        cfg.get('label') if cfg else None
    )
)

# DateTime widgets
WidgetRegistry.register(
    "datetime_relative",
    lambda obj, field, cfg: DateTimeDisplay.relative(
        getattr(obj, field),
        DateTimeDisplayConfig(**cfg) if cfg else None
    )
)

WidgetRegistry.register(
    "datetime_compact",
    lambda obj, field, cfg: DateTimeDisplay.compact(
        getattr(obj, field),
        DateTimeDisplayConfig(**cfg) if cfg else None
    )
)

# Simple widgets
WidgetRegistry.register(
    "text",
    lambda obj, field, cfg: str(getattr(obj, field, ""))
)

WidgetRegistry.register(
    "boolean",
    lambda obj, field, cfg: bool(getattr(obj, field, False))
)
