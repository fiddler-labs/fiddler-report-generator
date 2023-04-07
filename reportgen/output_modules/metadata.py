from .base import BaseOutput
from typing import Optional
from docx import Document
import os
import warnings


class Footer(BaseOutput):
    def __init__(self, text: str):
        self.text = text

    def render_pdf(self):
        pass

    def render_docx(self, document):
        section = document.sections[0]
        footer = section.footer
        footer_para = footer.paragraphs[0]
        print(footer_para)
        footer_para.text = self.text
