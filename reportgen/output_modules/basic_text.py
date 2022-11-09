from .base import BaseOutput
from .styles import BasicTextStyle
from docx.enum.text import WD_ALIGN_PARAGRAPH

class BasicText(BaseOutput):
    def __init__(self, text, style:BasicTextStyle=None):
        self.text = text
        if style:
            self.style = style
        else:
            self.style = BasicTextStyle()

    def render_pdf(self):
        pass

    def render_docx(self, document):
        #document.add_paragraph(self.text)
        paragraph = document.add_paragraph(self.text)

        if not self.style.alignment == 'center':
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        else:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
