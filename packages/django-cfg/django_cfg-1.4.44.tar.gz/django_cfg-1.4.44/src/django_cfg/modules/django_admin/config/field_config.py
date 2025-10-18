"""
Field configuration for declarative admin.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class FieldConfig(BaseModel):
    """
    Field display configuration.

    Describes how a field should be displayed in admin list view.
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    # Basic field info
    name: str = Field(..., description="Field name from model")
    title: Optional[str] = Field(None, description="Display title (defaults to field name)")

    # UI widget configuration
    ui_widget: Optional[str] = Field(
        None,
        description="Widget name: 'currency', 'badge', 'user_avatar', 'datetime_relative', etc."
    )

    # Display options
    header: bool = Field(False, description="Use header display (for users with avatar)")
    ordering: Optional[str] = Field(None, description="Field name for sorting")
    boolean: bool = Field(False, description="Treat as boolean field")
    empty_value: str = Field("—", description="Value to display when field is empty")

    # Widget-specific options (passed to widget config)
    # Currency widget
    currency: Optional[str] = Field(None, description="Currency code (USD, EUR, BTC)")
    precision: Optional[int] = Field(None, description="Decimal places for numbers")
    show_sign: Optional[bool] = Field(None, description="Show +/- sign for money")
    thousand_separator: Optional[bool] = Field(None, description="Use thousand separator")

    # Badge widget
    label_map: Optional[Dict[str, str]] = Field(
        None,
        description="Map values to badge variants: {'active': 'success', 'failed': 'danger'}"
    )
    variant: Optional[str] = Field(None, description="Badge variant: success, warning, danger, info")

    # Icon
    icon: Optional[str] = Field(None, description="Material icon name")

    # DateTime widget
    datetime_format: Optional[str] = Field(None, description="DateTime format string")
    show_relative: Optional[bool] = Field(None, description="Show relative time")

    # User widget
    show_email: Optional[bool] = Field(None, description="Show user email")
    show_avatar: Optional[bool] = Field(None, description="Show user avatar")
    avatar_size: Optional[int] = Field(None, description="Avatar size in pixels")

    # Advanced
    css_class: Optional[str] = Field(None, description="Custom CSS classes")
    tooltip: Optional[str] = Field(None, description="Tooltip text")

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract widget-specific configuration."""
        config = {}

        # Currency/Money config
        if self.currency is not None:
            config['currency'] = self.currency
        if self.precision is not None:
            config['decimal_places'] = self.precision
        if self.show_sign is not None:
            config['show_sign'] = self.show_sign
        if self.thousand_separator is not None:
            config['thousand_separator'] = self.thousand_separator

        # Badge config
        if self.label_map is not None:
            config['custom_mappings'] = self.label_map
        if self.variant is not None:
            config['variant'] = self.variant
        if self.icon is not None:
            config['icon'] = self.icon

        # DateTime config
        if self.datetime_format is not None:
            config['datetime_format'] = self.datetime_format
        if self.show_relative is not None:
            config['show_relative'] = self.show_relative

        # User config
        if self.show_email is not None:
            config['show_email'] = self.show_email
        if self.show_avatar is not None:
            config['show_avatar'] = self.show_avatar
        if self.avatar_size is not None:
            config['avatar_size'] = self.avatar_size

        return config
