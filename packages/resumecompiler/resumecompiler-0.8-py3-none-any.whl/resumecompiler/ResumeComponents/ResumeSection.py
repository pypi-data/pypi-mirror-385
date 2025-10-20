from bs4.element import Tag

from resumecompiler.Funcs.LatexFuncs import get_latex_command, indent_lines
from resumecompiler.ResumeComponents.ResumeComponent import ResumeComponent
from resumecompiler.ResumeComponents.ResumeItem import ResumeItem


class ResumeSection(ResumeComponent):
    def __init__(self, heading: str):
        super().__init__()

        self.heading = heading


def get_toolset_or_organisational_section_as_latex_lines(heading: str, resume_items: list[ResumeItem]) -> list[str]:
    """
    :param heading: The heading of the toolset or organisational section.
    :param resume_items: The list of resume items belonging to the toolset or organisational section.
    :return: The LaTeX representation of the resume section.
    """
    result = [
        get_latex_command("section", heading),
        get_latex_command("resumeSubheadingListStart")
    ]

    for resume_item in resume_items:
        result += indent_lines(resume_item.to_latex_lines())
        result.append("")

    result.append(get_latex_command("resumeSubheadingListEnd"))

    return result


def classify_tags_in_organisational_or_toolset_section_by_resume_item(tags: list[Tag]) -> list[list[Tag]]:
    """
    :param tags: A list of tags representing a series of resume items in a toolset or organisational section.
    :return: A two-dimensional list of tags, with each sublist containing the tags that belong to a resume item.
    """

    i = 0
    num_of_tags = len(tags)
    tags_by_resume_item: list[list[Tag]] = []

    while i < num_of_tags:
        if tags[i].name == "h3":
            tags_by_resume_item.append([tags[i]])
        else:
            tags_by_resume_item[-1].append(tags[i])
        i += 1

    return tags_by_resume_item