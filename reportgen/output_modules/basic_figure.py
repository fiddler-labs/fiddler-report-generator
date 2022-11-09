from .base import BaseOutput
from .styles import FigureStyle
from docx.shared import Inches
from typing import Optional

class BasicFigure(BaseOutput):
    def __init__(self, fig_path:str, style:Optional[FigureStyle]=None):
        self.path = fig_path
        if style:
            self.style = style
        else:
            self.style = FigureStyle()

    def render_pdf(self):
        pass

    def render_docx(self, document):
        document.add_picture(self.path, width=self.style.width)