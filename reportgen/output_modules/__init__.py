from .base import OutputTypes, BaseOutput
from .block import SimpleTextBlock, FormattedTextBlock, SimpleImage
from .styles import SimpleTextStyle, FormattedTextStyle
from .generate_output import generate_output

__all__ = ('OutputTypes', 'BaseOutput', 'generate_output', 'SimpleTextBlock','FormattedTextBlock','SimpleImage',
           'SimpleTextStyle', 'FormattedTextStyle')

# fiddler header color = rgb(0, 3, 80)
