import json
from .content import AtlassianPageContent


class AtlassianPage:
    def __init__(self, page_id: str, raw_content: dict):
        self.page_id = page_id
        self.raw_content = raw_content
        self.page_content = AtlassianPageContent(self.raw_content['body']['storage']['value'])

    def prettify(self) -> str:
        return json.dumps(self.get_page_content_dict(), indent=2)

    def get_page_id(self) -> str:
        return self.page_id

    def get_working_page_content(self) -> AtlassianPageContent:
        return self.page_content

    def get_page_content_dict(self) -> dict:
        content = self.raw_content
        content['body']['storage']['value'] = self.page_content.soup.__str__()

        return content

    def increase_version(self) -> None:
        """
        Takes a confluence page definition, extracts the version number and increases it
        """
        versionNumber = int(self.raw_content['version']['number'])
        versionedLink = str(self.raw_content['version']['_links']['self'])
        versionNumber += 1
        versionedLink = versionedLink[: versionedLink.rfind('/') + 1] + str(versionNumber)
        self.raw_content['version']['number'] = versionNumber
        self.raw_content['version']['_links']['self'] = versionedLink
