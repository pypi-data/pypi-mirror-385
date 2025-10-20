import markdown
from bs4 import BeautifulSoup
from bs4.element import Tag


def get_soup_from_markdown(markdown_contents: str) -> BeautifulSoup:
    """
    :param markdown_contents: The contents of a markdown file.
    :return: A BeautifulSoup object representing the markdown content parsed as HTML.
    """
    html = markdown.markdown(markdown_contents)
    return BeautifulSoup(html, "html.parser")


def get_children_tags(tag: Tag) -> list[Tag]:
    """
    :param tag: The parent tag from which to extract children.
    :return: A list of tags that are children of the given parent.
    """
    return [child for child in tag.children if isinstance(child, Tag)]
