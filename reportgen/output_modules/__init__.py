from .base import OutputTypes, BaseOutput
from .basic_text import BasicText
from .basic_figure import BasicFigure
from .styles import BasicTextStyle, Alignments, FigureStyle
from .generate_output import generate_output

__all__ = ('OutputTypes', 'BaseOutput', 'generate_output', 'BasicText','BasicFigure','BasicTextStyle', 'Alignments', 'FigureStyle')

# fiddler header color = rgb(0, 3, 80)
