from typing import List, Type, Optional
from docx import Document
from docxtpl import DocxTemplate
from .base import OutputTypes, BaseOutput
import warnings
import os

FIDDLER_DEFAULT_REPORT_NAME = 'fiddler_report'
DEFAULT_TEMPLATE_FILE = 'reportgen/templates/template.docx'


def _generate_output_docx(output_modules: List[BaseOutput], output_path: str, template: Optional[str]):

    template_file = template if template is not None else DEFAULT_TEMPLATE_FILE
    if os.path.isfile(template_file):
        document = DocxTemplate(template_file)
    else:
        warnings.warn(f'The template file {template_file} does not exist. The output is generated without a template.')
        document = Document()

    for output_module in output_modules:
        output_module.render_docx(document=document)

    if output_path is None:
        document.save(FIDDLER_DEFAULT_REPORT_NAME + '.docx')
    else:
        document.save(output_path)

    return None


def _generate_output_pdf(output_modules: List[Type[BaseOutput]], output_path: str):
    raise NotImplementedError('PDF not yet implemented.')


def generate_output(output_type: OutputTypes,
                    output_modules: List[Type[BaseOutput]],
                    output_path: str,
                    template: Optional[str] = None,
                    ):

    if output_type is OutputTypes.DOCX:
        output_processor = _generate_output_docx

    elif output_type is OutputTypes.PDF:
        output_processor = _generate_output_pdf

    else:
        raise ValueError('No such output type.')

    output_processor(output_modules=output_modules, output_path=output_path, template=template)
