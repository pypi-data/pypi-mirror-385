from typing import Union
import re

def indent_lines(lines: list[str]) -> list[str]:
    """
    :param lines: A list of lines.
    :return: A list of indented lines, each prefixed by a tab character.
    """
    return ['\t' + line for line in lines]


def format_date_range(string: str) -> str:
    """
    :param string: A string that represents a date range.
    :return: The same string except any sequence of consecutive hyphens ("-") and/or en dashes (U+2013 in Unicode) surrounded by spaces or digits is replaced by a pair of hyphens surrounded by spaces.

    Examples:
    "2012 - 2013" -> "2012 -- 2013"
    "Jan 2012 -- Dec 2013" -> "Jan 2012 -- Dec 2013"
    "2012 – Present" -> "2012 - Present"
    """
    return re.sub(r"[0-9\s][–\-]+[0-9\s]", r" -- ", string)


def get_latex_command(command: str, arguments: Union[str, list[str], None] = None,
                      square_bracket_options: Union[str, list[str], None] = None) -> str:
    """
    :param command: The name of a LaTeX command.
    :param arguments: The arguments passed to the LaTeX command. Each argument will be surrounded by curly braces.
    :param square_bracket_options: The options passed to the LaTeX command. The options will be separated by commas and surrounded by square brackets.
    :return: A line of LaTeX representing the command, with options and arguments as specified.
    """
    result = "\\" + command

    if square_bracket_options:
        result += "["
        if isinstance(square_bracket_options, str):
            result += square_bracket_options
        else:
            result += ", ".join(square_bracket_options)
        result += "]"

    if arguments:
        if isinstance(arguments, str):
            arguments = [arguments]

        result += "".join(map(lambda arg: "{" + arg + "}", arguments))

    return result


def get_latex_environment(env: str, contents: list[str], indent_contents: bool = True) -> list[str]:
    """
    :param env: The name of a LaTeX environment.
    :param contents: The contents of the LaTeX environment, expressed as a list of lines.
    :param indent_contents: Whether to indent the contents inside the environment.
    :return: A list of LaTeX lines representing the environment and its contents as specified.
    """
    result = ["\\begin{" + env + "}"]

    if indent_contents:
        result += indent_lines(contents)
    else:
        result += contents

    result.append("\\end{" + env + "}")

    return result
