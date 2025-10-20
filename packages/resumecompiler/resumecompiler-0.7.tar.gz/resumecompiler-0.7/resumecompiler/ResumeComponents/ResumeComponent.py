from abc import ABC, abstractmethod

class ResumeComponent(ABC):
    def __init__(self):
        """
        A ResumeComponent is an abstract base class that defines the interface of any part of a resume that can be compiled to LaTeX.
        """
        pass

    @abstractmethod
    def to_latex_lines(self) -> list[str]:
        """
        :return: The LaTeX code representation of this resume component.
        """
        pass