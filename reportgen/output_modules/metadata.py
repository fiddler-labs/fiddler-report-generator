from .base import BaseOutput
from typing import Optional
from docx import Document
import os
import warnings


class MetaDataContext(BaseOutput):
    def __init__(self, context_dict: dict):
        self.context_dict = context_dict

    def render_pdf(self):
        pass

    def render_docx(self, document):
        document.render(self.context_dict)


class Footer(BaseOutput):
    def __init__(self, text: str):
        self.text = text

    def render_pdf(self):
        pass

    def render_docx(self, document):
        section = document.sections[0]
        footer = section.footer
        footer_para = footer.paragraphs[0]
        footer_para.text = self.text
