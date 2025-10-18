"""Types for Admin Commands."""

from enum import Enum
from typing import Any, Optional

from madsci.common.types.base_types import Error, MadsciBaseModel
from pydantic import Field


class AdminCommands(str, Enum):
    """Valid Admin Commands to send to a Node"""

    SAFETY_STOP = "safety_stop"
    RESET = "reset"
    PAUSE = "pause"
    RESUME = "resume"
    CANCEL = "cancel"
    SHUTDOWN = "shutdown"
    LOCK = "lock"
    UNLOCK = "unlock"
    GET_LOCATION = "get_location"


class AdminCommandResponse(MadsciBaseModel):
    """Response from an Admin Command"""

    success: bool = Field(
        title="Admin Command Success",
        description="Whether the admin command was successful.",
        default=True,
    )
    errors: list[Error] = Field(
        title="Admin Command Errors",
        description="A list of errors that occurred while executing the admin command.",
        default_factory=list,
    )
    data: Optional[Any] = Field(
        title="Data", description="Any data returned by the admin action", default=None
    )
