"""
Field configuration for declarative admin.

Type-safe field configurations with widget-specific classes.
"""

from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# ===== Base Field Config =====

class FieldConfig(BaseModel):
    """
    Base field display configuration.

    Use specialized subclasses for type safety:
    - BadgeField: Badge widget with variants
    - CurrencyField: Currency/money display
    - DateTimeField: DateTime with relative time
    - UserField: User display with avatar
    - TextField: Simple text display
    - BooleanField: Boolean icons
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    # Basic field info
    name: str = Field(..., description="Field name from model")
    title: Optional[str] = Field(None, description="Display title (defaults to field name)")

    # UI widget configuration
    ui_widget: Optional[str] = Field(
        None,
        description="Widget name: 'badge', 'currency', 'user_avatar', 'datetime_relative', etc."
    )

    # Display options
    header: bool = Field(False, description="Use header display")
    ordering: Optional[str] = Field(None, description="Field name for sorting")
    empty_value: str = Field("—", description="Value to display when field is empty")

    # Icon
    icon: Optional[str] = Field(None, description="Material icon name")

    # Advanced
    css_class: Optional[str] = Field(None, description="Custom CSS classes")
    tooltip: Optional[str] = Field(None, description="Tooltip text")

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract widget-specific configuration."""
        config = {}
        if self.icon is not None:
            config['icon'] = self.icon
        return config


# ===== Specialized Field Configs =====

class BadgeField(FieldConfig):
    """
    Badge widget configuration.

    Examples:
        BadgeField(name="status", variant="success")
        BadgeField(name="type", label_map={'active': 'success', 'failed': 'danger'})
    """

    ui_widget: Literal["badge"] = "badge"

    variant: Optional[Literal["primary", "secondary", "success", "danger", "warning", "info"]] = Field(
        None,
        description="Badge color variant"
    )
    label_map: Optional[Dict[Any, str]] = Field(
        None,
        description="Map field values to badge variants: {'active': 'success', 'failed': 'danger'}"
    )

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract badge widget configuration."""
        config = super().get_widget_config()
        if self.variant is not None:
            config['variant'] = self.variant
        if self.label_map is not None:
            config['custom_mappings'] = self.label_map
        return config


class CurrencyField(FieldConfig):
    """
    Currency/money widget configuration.

    Examples:
        CurrencyField(name="price", currency="USD", precision=2)
        CurrencyField(name="balance", currency="BTC", precision=8, show_sign=True)
    """

    ui_widget: Literal["currency"] = "currency"

    currency: str = Field("USD", description="Currency code (USD, EUR, BTC)")
    precision: int = Field(2, description="Decimal places")
    show_sign: bool = Field(False, description="Show +/- sign")
    thousand_separator: bool = Field(True, description="Use thousand separator")

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract currency widget configuration."""
        config = super().get_widget_config()
        config['currency'] = self.currency
        config['decimal_places'] = self.precision
        config['show_sign'] = self.show_sign
        config['thousand_separator'] = self.thousand_separator
        return config


class DateTimeField(FieldConfig):
    """
    DateTime widget configuration.

    Examples:
        DateTimeField(name="created_at", show_relative=True)
        DateTimeField(name="updated_at", datetime_format="%Y-%m-%d %H:%M")
    """

    ui_widget: Literal["datetime_relative"] = "datetime_relative"

    datetime_format: Optional[str] = Field(None, description="DateTime format string")
    show_relative: bool = Field(True, description="Show relative time (e.g., '2 hours ago')")

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract datetime widget configuration."""
        config = super().get_widget_config()
        if self.datetime_format is not None:
            config['datetime_format'] = self.datetime_format
        config['show_relative'] = self.show_relative
        return config


class UserField(FieldConfig):
    """
    User display widget configuration.

    Examples:
        UserField(name="owner", ui_widget="user_avatar", show_email=True)
        UserField(name="created_by", ui_widget="user_simple")
    """

    ui_widget: Literal["user_avatar", "user_simple"] = "user_avatar"

    show_email: bool = Field(True, description="Show user email")
    show_avatar: bool = Field(True, description="Show user avatar")
    avatar_size: int = Field(32, description="Avatar size in pixels")

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract user widget configuration."""
        config = super().get_widget_config()
        config['show_email'] = self.show_email
        config['show_avatar'] = self.show_avatar
        config['avatar_size'] = self.avatar_size
        return config


class TextField(FieldConfig):
    """
    Simple text widget configuration.

    Examples:
        TextField(name="description")
        TextField(name="email", icon=Icons.EMAIL)
    """

    ui_widget: Literal["text"] = "text"


class BooleanField(FieldConfig):
    """
    Boolean widget configuration.

    Examples:
        BooleanField(name="is_active")
        BooleanField(name="is_verified", icon=Icons.CHECK_CIRCLE)
    """

    ui_widget: Literal["boolean"] = "boolean"

    true_icon: Optional[str] = Field(None, description="Icon for True value")
    false_icon: Optional[str] = Field(None, description="Icon for False value")

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract boolean widget configuration."""
        config = super().get_widget_config()
        if self.true_icon is not None:
            config['true_icon'] = self.true_icon
        if self.false_icon is not None:
            config['false_icon'] = self.false_icon
        return config
