from abc import abstractmethod

from resumecompiler.ResumeComponents.ResumeComponent import ResumeComponent
from resumecompiler.Funcs.LatexFuncs import indent_lines, get_latex_command


class ResumeItem(ResumeComponent):
    def __init__(self, subheading: str, description_list: list[str]):
        """
        :param subheading: The subheading of this resume item.
        :param description_list: The description list of this resume item.
        """
        super().__init__()
        self.subheading = subheading
        self.description_list = description_list

    def get_description_list_as_latex_lines(self) -> list[str]:
        """
        :return: The LaTeX representation of this resume item's description list.
        """
        result = [get_latex_command("resumeDescriptionListStart")]

        result += indent_lines(
            [get_latex_command("resumeDescriptionListItem", desc_list_item) for desc_list_item in self.description_list]
        )

        result.append(get_latex_command("resumeDescriptionListEnd"))

        return result

    def to_latex_lines(self) -> list[str]:
        if self.subheading.startswith("^"):  # Hidden resume item
            return [""]

        return self.to_latex_lines_assuming_not_hidden()

    @abstractmethod
    def to_latex_lines_assuming_not_hidden(self) -> list[str]:
        pass