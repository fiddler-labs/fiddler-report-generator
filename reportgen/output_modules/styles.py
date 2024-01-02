from dataclasses import dataclass


@dataclass
class SimpleTextStyle:
    alignment: str = 'left'
    size: int = 12
    font_style: str =None


@dataclass
class FormattedTextStyle:
    alignment: str = 'left'