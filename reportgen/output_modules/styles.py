from dataclasses import dataclass
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