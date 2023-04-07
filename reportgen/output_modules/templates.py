from typing import Optional
from docx import Document
from docxtpl import DocxTemplate
import os
from datetime import datetime, timezone
import warnings


DEFAULT_TEMPLATE_FILE = 'reportgen/templates/template.docx'


def docx_from_template(template: Optional[str], author: Optional[str]):

    template_file = template if template is not None else DEFAULT_TEMPLATE_FILE

    if os.path.isfile(template_file):
        document = DocxTemplate(template_file)
        date = datetime.now(timezone.utc)
        footer_metadata = f'Generated on {date.strftime("%B %d, %Y at %H:%M UTC")} '
        if author:
            footer_metadata += f'by {author}'
        context = {'footer_metadata': footer_metadata}
        document.render(context)
    else:
        warnings.warn(f'The template file {template_file} does not exist. The output is generated without a template.')
        document = Document()

    return document
