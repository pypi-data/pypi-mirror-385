"""
Action configuration for declarative admin.
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ActionConfig(BaseModel):
    """
    Admin action configuration.

    Defines custom actions for admin list view.
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    name: str = Field(..., description="Action function name")
    description: str = Field(..., description="Action description shown in UI")
    variant: str = Field("default", description="Button variant: default, success, warning, danger, primary")
    icon: Optional[str] = Field(None, description="Material icon name")
    confirmation: bool = Field(False, description="Require confirmation before execution")
    handler: str = Field(..., description="Python path to action handler function")
    permissions: List[str] = Field(default_factory=list, description="Required permissions")

    def get_handler_function(self):
        """Import and return the handler function."""
        import importlib

        module_path, function_name = self.handler.rsplit('.', 1)
        module = importlib.import_module(module_path)
        return getattr(module, function_name)
