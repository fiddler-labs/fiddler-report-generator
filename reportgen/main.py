from typing import List, Type
from .output_modules import OutputTypes
from .analysis_modules import BaseAnalysis
from .output_modules import BaseOutput
from .output_modules import generate_output


def _run_analyses(
    fiddler_api, analysis_modules: List[BaseAnalysis]
) -> List[Type[BaseOutput]]:

    for analysis_module in analysis_modules:
        analysis_module.preflights(fiddler_api)

    output_modules = []
    for analysis_module in analysis_modules:
        output_modules = output_modules + analysis_module.run(fiddler_api)

    return output_modules


def generate_report(
    fiddler_api,
    analysis_modules: List[BaseAnalysis],
    output_type: OutputTypes,
    output_path=None,
):
    output_modules = _run_analyses(
        fiddler_api=fiddler_api, analysis_modules=analysis_modules
    )

    generate_output(
        output_type=output_type, output_modules=output_modules, output_path=output_path
    )

    return None
