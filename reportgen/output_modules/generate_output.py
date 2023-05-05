from typing import List, Type, Optional
from docx import Document
from docxtpl import DocxTemplate
from .base import OutputTypes, BaseOutput
import warnings
import os
from docx2pdf import convert


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

    report_name = FIDDLER_DEFAULT_REPORT_NAME + '.docx' if output_path is None else output_path + '.docx'
    document.save(report_name)
    return None


def _generate_output_pdf(output_modules: List[BaseOutput], output_path: str, template: Optional[str]):
    template_file = template if template is not None else DEFAULT_TEMPLATE_FILE
    _generate_output_docx(output_modules=output_modules, output_path='tmp', template=template_file)

    report_name = FIDDLER_DEFAULT_REPORT_NAME + '.pdf' if output_path is None else output_path + '.pdf'
    file = open(report_name, "w")
    file.close()
    convert('tmp.docx', report_name)
    return None


def generate_output(output_types: List[OutputTypes],
                    output_modules: List[Type[BaseOutput]],
                    output_path: str,
                    template: Optional[str] = None,
                    ):

    for type in output_types:

        if type is OutputTypes.DOCX:
            output_processor = _generate_output_docx

        elif type is OutputTypes.PDF:
            output_processor = _generate_output_pdf

        else:
            raise ValueError('No such output type.')

    output_processor(output_modules=output_modules, output_path=output_path, template=template)
