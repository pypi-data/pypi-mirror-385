from bs4 import Tag

from resumecompiler.ResumeComponents.ResumeSection import ResumeSection
from resumecompiler.Funcs.HtmlFuncs import get_children_tags
from resumecompiler.Funcs.LatexFuncs import get_latex_command


class CatalogueSection(ResumeSection):
    def __init__(self, tags: list[Tag]):
        """
        :param tags: A list of HTML tags that belong to this catalogue section.
        """
        heading = tags[0].text
        super().__init__(heading=heading)

        # Initialise the list under this catalogue section
        self.catalogue_list = []

        i = 1
        while i < len(tags):
            if tags[i].name == "ul":
                self.catalogue_list += [list_item.text for list_item in get_children_tags(tags[i]) if list_item.name == "li"]
            i += 1

    def to_latex_lines(self) -> list[str]:
        result = [get_latex_command("section", self.heading)]

        if not self.catalogue_list:
            return result

        result.append("")
        result.append("\\begin{itemize}[leftmargin=0.15in, label={}]\small{\item{")

        # Detect and parse labels in each list item
        # [Label]: [thing], [thing], ...
        for list_item in self.catalogue_list:
            list_item_split_by_colon = list_item.split(":", maxsplit=1)
            if len(list_item_split_by_colon) == 2:  # If there is a colon
                label, text = list_item_split_by_colon
                latex_line = get_latex_command(command="textbf", arguments=label) + ":" + text
            else:
                latex_line = list_item
            result.append("\t" + latex_line + r"\\")

        result.append(r"}}\end{itemize}")

        return result