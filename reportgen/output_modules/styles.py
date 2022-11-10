from dataclasses import dataclass
from typing import Optional

@dataclass
class SimpleTextStyle:
    alignment: str='left'
    size: int=14
    font_style: str=None


@dataclass
class FormattedTextStyle:
    alignment: str='left'
    size: int = 14