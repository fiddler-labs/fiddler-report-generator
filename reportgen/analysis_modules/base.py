from abc import ABC, abstractmethod
from ..output_modules import BaseOutput
from typing import List, Type


class BaseAnalysis(ABC):
    @abstractmethod
    def run(self, api) -> List[Type[BaseOutput]]:
        pass
