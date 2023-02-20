from .base import OutputTypes, BaseOutput
from .blocks import SimpleTextBlock, FormattedTextBlock, SimpleImage, Table, AddBreak, AddPageBreak
from .styles import SimpleTextStyle, FormattedTextStyle
from .generate_output import generate_output
from .tmp_file import  TempOutputFile

__all__ = ('OutputTypes', 'BaseOutput', 'generate_output', 'SimpleTextBlock','FormattedTextBlock','SimpleImage',
           'SimpleTextStyle', 'FormattedTextStyle', 'TempOutputFile', 'Table', 'AddBreak', 'AddPageBreak')

# fiddler header color = rgb(0, 3, 80)
