from typing import Any

from bs4 import Tag

from resumecompiler.ResumeComponents.ResumeItem import ResumeItem
from resumecompiler.Funcs.Funcs import take_fixed_num_of_input_strings, take_fixed_num_of_inputs_with_same_default
from resumecompiler.Funcs.HtmlFuncs import get_children_tags
from resumecompiler.Funcs.LatexFuncs import get_latex_command, format_date_range


class ToolsetSectionResumeItem(ResumeItem):
    def __init__(self, tags: list[Tag]):
        tags = take_fixed_num_of_inputs_with_same_default(tags, 3, None)

        subheading = tags[0].text if tags[0] else ""
        pre_block_contents = tags[1].text if tags[1] else ""
        description_list = [item.text for item in get_children_tags(tags[2])] if tags[2] else []

        super().__init__(subheading=subheading, description_list=description_list)

        # Two pieces of auxiliary info - tools and time
        # If more than two are provided, only the first two pieces of information are accepted as input
        # If less than two are provided, we pad them with empty strings
        num_of_auxiliary_info = 2
        pre_block_lines = pre_block_contents.split("\n", maxsplit=num_of_auxiliary_info)

        self.tools, self.time = take_fixed_num_of_input_strings(pre_block_lines, num_of_auxiliary_info)

    def to_latex_lines_assuming_not_hidden(self) -> list[str]:
        # Resume subheading with toolset and time
        result = [
            get_latex_command(
                command="resumeItemSubheadingWithToolset",
                arguments=[
                    get_latex_command(command="textbf", arguments=self.subheading) + " $|$ " + get_latex_command(
                        command="emph", arguments=self.tools),
                    format_date_range(self.time)
                ]
            )
        ]

        if self.description_list:
            result.append("")
            result += self.get_description_list_as_latex_lines()

        return result

    def to_json_like_dict(self) -> dict[str, Any]:
        return {
            "subheading": self.subheading,
            "tools": self.tools,
            "time": self.time,
            "description_list": self.description_list,
        }
