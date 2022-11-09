from dataclasses import dataclass
from typing import Optional
import enum

@enum.unique
class Alignments(enum.Enum):
    LEFT = 'left'
    CENTER = 'center'
    RIGHT =  'right'


@dataclass
class BasicTextStyle:
    alignment: Alignments=Alignments.LEFT
    bold: bool=False
    size: int=14


@dataclass
class FigureStyle:
    width: Optional[int]=None