from abc import ABC, abstractmethod
from typing import List, Type

from ..output_modules import BaseOutput


class BaseAnalysis(ABC):
    @abstractmethod
    def preflight(self, api, project_id):
        """
        The preflight method of all  analysis modules will be run by the report generator before running the actual
        run function in order to catch errors that can be detected without running the module fully. This process
        reduces the rate of failures that happen after a significant time after the report generation has started.
        """
        pass

    @abstractmethod
    def run(self, api) -> List[Type[BaseOutput]]:
        pass
