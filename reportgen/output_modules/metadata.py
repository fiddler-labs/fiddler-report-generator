from .base import BaseOutput


class MetaDataContext(BaseOutput):
    """
    An output module that replaces the jinja2 tags in the template documents by the values specified in
    a context dictionary.
    """
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
