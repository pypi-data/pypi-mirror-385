from pathlib import Path
from typing import Any


def strip_strings(strings: list[str]) -> list[str]:
    """
    :param strings: A list of strings.
    :return: A list of strings that have been stripped. Strings that contain only whitespaces are removed.
    """
    result = []

    for s in strings:
        stripped = s.strip()
        if stripped:
            result.append(stripped)

    return result


def take_fixed_num_of_inputs_with_defaults(inputs: list, defaults: list) -> list:
    """
    :param inputs: A list of inputs.
    :param defaults: A list of default values.
    :return: A list with the same length as default.
    If len(inputs) < len(default), the original list is padded using the default values at the corresponding indices.
    If len(inputs) == len(default), the original list is returned with no changes made.
    If len(inputs) > len(default), the original list is cut off early to match the length of the default list.
    """

    return [inputs[i] if i < len(inputs) else default for i, default in enumerate(defaults)]


def take_fixed_num_of_inputs_with_same_default(inputs: list, n: int, default: Any) -> list:
    """
    :param inputs: A list of inputs.
    :param n: The number of inputs to accept.
    :param default: The default input value to use for padding.
    :return: A list of n inputs.
    If len(inputs) < n, the original list is padded using the default value until its length is n.
    If len(inputs) == n, the original list is returned with no changes made.
    If len(inputs) > n, a list containing the first n inputs in the original list is returned.
    """

    return [inputs[i] if i < len(inputs) else default for i in range(n)]


def take_fixed_num_of_input_strings(inputs: list[str], n: int) -> list[str]:
    """
    :param inputs: A list of input strings.
    :param n: The number of input strings to accept.
    :return: A list of n strings.
    If len(inputs) < n, the original list is padded until its length is n.
    If len(inputs) == n, the original list is returned with no changes made.
    If len(inputs) > n, a list containing the first n strings in the original list is returned.
    """

    return take_fixed_num_of_inputs_with_same_default(inputs, n, "")


def create_and_write_file(file_path: Path, contents: str):
    """
    :param file_path: A file path.
    :param contents: Contents to be written onto the file.
    :return: Creates the file (along with all intermediate directories) and writes the specified contents onto the file.
    """
    # Create parent directories if they don't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Write content to the file
    file_path.write_text(contents)