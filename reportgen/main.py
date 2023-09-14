from typing import List, Type, Optional
from tqdm import tqdm
from .output_modules import OutputTypes
from .analysis_modules import BaseAnalysis
from .analysis_modules import MetaData
from .output_modules import BaseOutput
from .output_modules import generate_output
import fiddler as fdl
import warnings


class FiddlerReportGenerator:
    """
    The Fiddler report generator main class. An instance of this class can be initiated by passing an instance
    of the Fiddler client or by specifying the information that is needed to connect to a Fiddler deployment.
    Furthermore, this class stores the report metadata such as author name etc. The generate_report method of this
    class is used to generate a report by passing the list of analysis modules to be added to the report.
    """
    def __init__(self,
                 fiddler_api=None,
                 url: Optional[str] = None,
                 org_id: Optional[str] = None,
                 auth_token: Optional[str] = None,
                 author: Optional[str] = None,
                 ):
        self.author = author

        if fiddler_api:
            if 'add_model' in dir(fiddler_api):
                self.fiddler_api = fiddler_api
            else:
                raise TypeError('fiddler_api argument can only accept an instance of the Fiddler client.')

            if any([url, org_id, auth_token]):
                warnings.warn(
                    f'Connection information arguments are ignored since a Fiddler client object is passed to '
                    'the report generator.'
                )

        else:
            if all([url, org_id, auth_token]):
                self.fiddler_api = fdl.FiddlerApi(url=url,
                                                  org_id=org_id,
                                                  auth_token=auth_token
                                                  )
            else:
                raise ValueError('All connection information (url, org_id, auth_token) or '
                                 'a Fiddler client object is required to initiate report generator.')

    def _run_analyses(self,
                      analysis_modules: List[BaseAnalysis],
                      project_id,
                      ) -> List[Type[BaseOutput]]:
        for analysis_module in analysis_modules:
            analysis_module.preflight(self.fiddler_api, project_id)

        output_modules = []
        pbar = tqdm(total=len(analysis_modules), desc='Running analysis modules')
        for analysis_module in analysis_modules:
            output_modules = output_modules + analysis_module.run(self.fiddler_api)
            pbar.update()

        return output_modules

    def generate_report(self,
                        project_id: Optional[str] = None,
                        analysis_modules: List[BaseAnalysis] = [],
                        output_type: OutputTypes = OutputTypes.DOCX,
                        output_path=None,
                        template=None
                        ):

        output_modules = []
        output_modules += MetaData(author=self.author).run(self.fiddler_api)
        output_modules += self._run_analyses(analysis_modules, project_id)

        generate_output(output_type=output_type,
                        output_modules=output_modules,
                        output_path=output_path,
                        template=template,
                        )
