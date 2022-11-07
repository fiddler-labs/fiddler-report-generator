from typing import List, Type
from .base import OutputTypes, BaseOutput


def _generate_output_docx(
    output_type: OutputTypes, output_modules: List[Type[BaseOutput]]
):
    return


def _generate_output_pdf(
    output_type: OutputTypes, output_modules: List[Type[BaseOutput]]
):
    raise NotImplementedError('PDF not yet implemented.')


def generate_output(output_type: OutputTypes, output_modules: List[Type[BaseOutput]]):

    if output_type is OutputTypes.DOCX:
        output_processor = _generate_output_docx

    elif output_type is OutputTypes.PDF:
        output_processor = _generate_output_pdf

    else:
        raise ValueError('No such output type.')

    output_processor(output_type=output_type, output_modules=output_modules)
