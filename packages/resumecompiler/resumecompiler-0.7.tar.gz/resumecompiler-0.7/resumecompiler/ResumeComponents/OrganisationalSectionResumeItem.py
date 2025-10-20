from typing import Any

from bs4 import Tag

from resumecompiler.ResumeComponents.ResumeItem import ResumeItem
from resumecompiler.Funcs.Funcs import take_fixed_num_of_input_strings, take_fixed_num_of_inputs_with_same_default
from resumecompiler.Funcs.HtmlFuncs import get_children_tags
from resumecompiler.Funcs.LatexFuncs import get_latex_command, format_date_range


class OrganisationalSectionResumeItem(ResumeItem):
    def __init__(self, tags: list[Tag]):
        """
        :param tags: A list of HTML tags that belong to this organisation section resume item.
        """
        tags = take_fixed_num_of_inputs_with_same_default(tags, 3, None)

        subheading = tags[0].text if tags[0] else ""
        pre_block_contents = tags[1].text if tags[1] else ""
        description_list = [item.text for item in get_children_tags(tags[2])] if tags[2] else []

        super().__init__(subheading=subheading, description_list=description_list)

        # Parse preformatted block as exactly three pieces of auxiliary information
        # If more than three are provided, only the first three pieces of information are accepted as input
        # If less than three are provided, we pad them with empty strings

        num_of_auxiliary_info = 3
        pre_block_lines = pre_block_contents.split("\n")[:num_of_auxiliary_info]

        self.first_row_right, self.second_row_left, self.second_row_right = take_fixed_num_of_input_strings(pre_block_lines, num_of_auxiliary_info)

        self.first_row_right = format_date_range(self.first_row_right)
        self.second_row_right = format_date_range(self.second_row_right)

    def to_latex_lines_assuming_not_hidden(self) -> list[str]:
        # Resume subheading with auxiliary info
        result = [
            get_latex_command(
                command="resumeItemSubheading",
                arguments=[self.subheading, self.first_row_right, self.second_row_left, self.second_row_right]
            )
        ]

        if self.description_list:
            result.append("")
            result += self.get_description_list_as_latex_lines()

        return result

    def to_json_like_dict(self) -> dict[str, Any]:
        return {
            "subheading": self.subheading,
            "first_row_right": self.first_row_right,
            "second_row_left": self.second_row_left,
            "second_row_right": self.second_row_right,
            "description_list": self.description_list,
        }