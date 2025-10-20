from bs4.element import Tag

from resumecompiler.ResumeComponents.ResumeComponent import ResumeComponent
from resumecompiler.Funcs.HtmlFuncs import get_children_tags
from resumecompiler.Funcs.LatexFuncs import get_latex_environment, get_latex_command

class ContactList(ResumeComponent):
    def __init__(self, ul_tag: Tag):
        """
        :param ul_tag: The unordered list tag that represents this contact list.
        """
        super().__init__()

        # First value of tuple: displayed text
        # Second value of tuple: Linked site (possibly empty if the contact list item is not a hyperlink)
        self.contacts: list[tuple[str, str]] = []

        for li_tag in get_children_tags(ul_tag):
            first_hyperlink = li_tag.find("a", href=True)  # Returns None if no hyperlink found
            if first_hyperlink:
                self.contacts.append((first_hyperlink.text, first_hyperlink.get("href")))
            else:
                self.contacts.append((li_tag.text, ""))

    def to_latex_lines(self) -> list[str]:
        centered_lines: list[str] = [r"\small"]

        num_of_contacts = len(self.contacts)
        for i in range(num_of_contacts):
            displayed_text, link = self.contacts[i]
            if link:  # Link is non-empty
                centered_lines.append(
                    get_latex_command(
                        command="href",
                        arguments=[link, get_latex_command(command="underline", arguments=displayed_text)]
                    )
                )
            else:
                centered_lines.append(displayed_text)

            if i != num_of_contacts - 1:
                centered_lines.append(r"$|$")

        return get_latex_environment(env="center", contents=centered_lines)