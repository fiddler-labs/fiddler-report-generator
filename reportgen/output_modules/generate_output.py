from docx import Document
from typing import List, Type
from .base import OutputTypes, BaseOutput

FIDDLER_DEFAULT_REPORT_NAME = 'fiddler_report'


def _generate_output_docx(output_modules: List[BaseOutput], output_path: str):
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


def generate_output(
    output_type: OutputTypes, output_modules: List[Type[BaseOutput]], output_path: str
):

    if output_type is OutputTypes.DOCX:
        output_processor = _generate_output_docx

    elif output_type is OutputTypes.PDF:
        output_processor = _generate_output_pdf

    else:
        raise ValueError('No such output type.')

    output_processor(output_modules=output_modules, output_path=output_path)
