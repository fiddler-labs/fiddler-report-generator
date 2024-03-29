import os
import warnings
from typing import List, Type, Optional

from docx import Document
from docx2pdf import convert
from docxtpl import DocxTemplate
from pkg_resources import resource_filename

from .base import OutputTypes, BaseOutput

FIDDLER_DEFAULT_REPORT_NAME = 'fiddler_report'
DEFAULT_TEMPLATE_FILE = resource_filename('reportgen', 'templates/template.docx')

def _generate_output_docx(output_modules: List[BaseOutput], output_path: str, template: Optional[str]):

    template_file = template if template is not None else DEFAULT_TEMPLATE_FILE
    if os.path.isfile(template_file):
        document = DocxTemplate(template_file)
    else:
        warnings.warn(f'The template file {template_file} does not exist. The output is generated without a template.')
        document = Document()

    for output_module in output_modules:
        output_module.render_docx(document=document)

    report_name = FIDDLER_DEFAULT_REPORT_NAME + '.docx' if output_path is None else output_path + '.docx'
    document.save(report_name)
    return None


def _generate_output_pdf(output_modules: List[BaseOutput], output_path: str, template: Optional[str]):
    template_file = template if template is not None else DEFAULT_TEMPLATE_FILE
    _generate_output_docx(output_modules=output_modules, output_path='tmp/tmp', template=template_file)

    report_name = FIDDLER_DEFAULT_REPORT_NAME + '.pdf' if output_path is None else output_path + '.pdf'
    file = open(report_name, "w")
    file.close()
    convert('tmp/tmp.docx', report_name)
    return None


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
