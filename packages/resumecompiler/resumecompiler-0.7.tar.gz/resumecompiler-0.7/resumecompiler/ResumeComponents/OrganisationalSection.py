from typing import Any

from bs4 import Tag

from resumecompiler.ResumeComponents.OrganisationalSectionResumeItem import OrganisationalSectionResumeItem
from resumecompiler.ResumeComponents.ResumeSection import ResumeSection, get_toolset_or_organisational_section_as_latex_lines, classify_tags_in_organisational_or_toolset_section_by_resume_item


class OrganisationalSection(ResumeSection):
    def __init__(self, tags: list[Tag]):
        """
        :param tags: A list of HTML tags that belong to this organisational section.
        """
        heading = tags[0].text

        super().__init__(heading=heading)

        tags_by_resume_item = classify_tags_in_organisational_or_toolset_section_by_resume_item(tags[1:])

        # Initialise resume items
        self.resume_items: list[OrganisationalSectionResumeItem] = [
            OrganisationalSectionResumeItem(tags_for_resume_item) for tags_for_resume_item in tags_by_resume_item
        ]

    def to_latex_lines(self) -> list[str]:
        return get_toolset_or_organisational_section_as_latex_lines(heading=self.heading, resume_items=self.resume_items)

    def to_json_like_dict(self) -> dict[str, Any]:
        return {
            "heading": self.heading,
            "type": "organisational",
            "resume_items": [resume_item.to_json_like_dict() for resume_item in self.resume_items],
        }