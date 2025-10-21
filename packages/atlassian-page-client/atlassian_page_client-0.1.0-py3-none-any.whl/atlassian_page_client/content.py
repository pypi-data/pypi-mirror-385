from bs4 import BeautifulSoup
import bs4


class AtlassianPageContent:
    def __init__(self, raw_html: str):
        self.raw_html = raw_html
        self.soup = BeautifulSoup(raw_html, 'html.parser')

    def get_root(self) -> bs4.element.Tag:
        return self.soup

    def prettify(self) -> str:
        return self.soup.prettify()

    def find_by_Attribute(self, attribute_name: str, value: str) -> bs4.element.Tag:
        # callback to find by
        def byAttribute(tag: bs4.element.Tag) -> bool:
            return tag.has_attr(attribute_name) and tag.get_attribute_list(attribute_name)[0] == value
        
        return self.soup.find(byAttribute)

    def new_tag(self, tag_name: str, **kwargs) -> bs4.element.Tag:
        return self.soup.new_tag(tag_name, **kwargs)
