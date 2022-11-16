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

    def render_pdf(self):
        pass

    def render_docx(self, p):
        p.add_run(self.text)


class BoldText(FormattedText):
    def __init__(self, text:str):
        self.text = text

    def render_pdf(self):
        pass

    def render_docx(self, p):
        p.add_run(self.text).font.bold = True


class ItalicText(FormattedText):
    def __init__(self, text:str):
        self.text = text

    def render_pdf(self):
        pass

    def render_docx(self, p):
        p.add_run(self.text).font.italic = True


class URL(FormattedText):
    def __init__(self, text:str, url:str):
        self.text = text
        self.url = url

    def render_pdf(self):
        pass

    def render_docx(self, p):
        pass
        #it seems that python-docx does not have add_hyperlink yet. We can write something manually if needed
        #p.add_hyperlink(text=self.text, url=self.url)