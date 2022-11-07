from .base import BaseOutput


class BasicText(BaseOutput):
    def __init__(self, text):
        self.text = text

    def render_pdf(self):
        pass

    def render_docx(self):
        pass
