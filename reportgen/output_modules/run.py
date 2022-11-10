from .base import BaseOutput
from typing import Optional
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from docx.shared import Inches


class FormattedText(BaseOutput):
    pass


class PlainText(FormattedText):
    def __init__(self, text:str):
        self.text = text

    def render_docx(self, document):
        pass


class BoldText(FormattedText):
    def __init__(self, text:str):
        self.text = text

    def render_docx(self, document):
        pass


class ItalicText(FormattedText):
    def __init__(self, text:str):
        self.text = text

    def render_docx(self, document):
        pass


class URL(FormattedText):
    def __init__(self, text:str):
        self.text = text

    def render_docx(self, document):
        pass