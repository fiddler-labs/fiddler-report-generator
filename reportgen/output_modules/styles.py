from dataclasses import dataclass
from typing import Optional

@dataclass
class SimpleTextStyle:
    alignment='left'
    size: int = 14
    font_style=None


@dataclass
class FormattedTextStyle:
    alignment='left'
    size: int = 14