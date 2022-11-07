from abc import ABC, abstractmethod
import enum


@enum.unique
class OutputTypes(enum.Enum):
    PDF = 0
    DOCX = 1


class BaseOutput(ABC):
    def render(self, api) -> str:
        pass

    @abstractmethod
    def render_pdf(self):
        pass

    @abstractmethod
    def render_docx(self):
        pass
