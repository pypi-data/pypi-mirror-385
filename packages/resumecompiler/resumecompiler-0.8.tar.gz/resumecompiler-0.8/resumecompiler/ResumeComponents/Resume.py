from bs4.element import Tag

from pathlib import Path
import json

from resumecompiler.Funcs.Funcs import create_and_write_file
from resumecompiler.ResumeComponents.CatalogueSection import CatalogueSection
from resumecompiler.ResumeComponents.ResumeComponent import ResumeComponent
from resumecompiler.ResumeComponents.OrganisationalSection import OrganisationalSection
from resumecompiler.ResumeComponents.Title import Title
from resumecompiler.ResumeComponents.ContactList import ContactList
from resumecompiler.ResumeComponents.ResumeSection import ResumeSection
from resumecompiler.ResumeComponents.ToolsetSection import ToolsetSection
from resumecompiler.Funcs.HtmlFuncs import get_soup_from_markdown, get_children_tags
from resumecompiler.Funcs.LatexFuncs import get_latex_environment
from resumecompiler.Enums.Font import Font


class Resume(ResumeComponent):
    def __init__(self, markdown_contents: str):
        """
        :param markdown_contents: The markdown content to be compiled.
        """
        super().__init__()

        soup = get_soup_from_markdown(markdown_contents)
        tags = get_children_tags(soup)

        num_of_tags = len(tags)

        # Classify tags by section
        i = 0
        tags_prior_to_first_section: list[Tag] = []
        tags_by_section: list[list[Tag]] = []

        while i < num_of_tags and tags[i].name != "h2":
            tags_prior_to_first_section.append(tags[i])
            i += 1

        while i < num_of_tags:
            if tags[i].name == "h2":
                tags_by_section.append([tags[i]])
            else:
                tags_by_section[-1].append(tags[i])
            i += 1

        # Parse components
        self.components: list[ResumeComponent] = []

        for tag in tags_prior_to_first_section:
            if tag.name == "h1":  # Title
                self.components.append(Title(tag))
            elif tag.name == "ul":  # Contact list
                self.components.append(ContactList(tag))

        for tags_in_section in tags_by_section:
            self.components.append(get_resume_section_from_tags(tags_in_section))

    def to_latex_lines(self, font: Font = Font.TIMES_NEW_ROMAN) -> list[str]:
        result: list[str] = []

        with open(Path(__file__).parent.joinpath("preamble.tex"), "r") as preamble_file:
            while True:
                line = preamble_file.readline()

                if not line:
                    break

                line = line.removesuffix('\n')

                if line == "% FONT CHOICE GOES HERE":
                    line = font.value

                result.append(line)

        result.append("")

        document_contents = []
        for component in self.components:
            document_contents += component.to_latex_lines()
            for _ in range(3):
                document_contents.append("")

        result += get_latex_environment(env="document", contents=document_contents, indent_contents=False)

        return result


def get_resume_section_from_tags(tags: list[Tag]) -> ResumeSection:
    """
    :param tags: A list of HTML tags that belong to a resume section.
    :return: The parsed resume section to which the inputted tags belong.
    """
    # Identify the section type
    heading = tags[0].text

    if len(heading) > 0 and heading[0] == "!":
        return ToolsetSection(tags)
    elif any(map(lambda t: t.name == "h3", tags)):
        return OrganisationalSection(tags)
    else:
        return CatalogueSection(tags)