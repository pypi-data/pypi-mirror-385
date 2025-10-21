"""Backward compatible entry point for tgwrap."""

from __future__ import annotations

from .core.constants import STAGES
from .core.wrapper import TgWrap

__all__ = ["STAGES", "TgWrap"]
