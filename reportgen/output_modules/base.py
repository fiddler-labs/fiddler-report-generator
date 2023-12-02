import enum
from abc import ABC, abstractmethod


@enum.unique
class OutputTypes(enum.Enum):
    PDF = 0
    DOCX = 1


class BaseOutput(ABC):
    @abstractmethod
    def render_pdf(self):
        pass

    @abstractmethod
    def render_docx(self, document):
        pass
