from .base import OutputTypes, BaseOutput
from .blocks import SimpleTextBlock, FormattedTextBlock, SimpleImage, Table, AddBreak, AddPageBreak
from .styles import SimpleTextStyle, FormattedTextStyle
from .text_styles import PlainText, BoldText, ItalicText
from .generate_output import generate_output
from .tmp_file import TempOutputFile
from .charts import LinePlot
from .metadata import Footer

__all__ = ('OutputTypes', 'BaseOutput', 'generate_output', 'SimpleTextBlock','FormattedTextBlock','SimpleImage',
           'SimpleTextStyle', 'FormattedTextStyle', 'TempOutputFile', 'Table', 'AddBreak', 'AddPageBreak', 'LinePlot',
           'PlainText', 'BoldText', 'ItalicText', 'Footer')

# fiddler header color = rgb(0, 3, 80)
