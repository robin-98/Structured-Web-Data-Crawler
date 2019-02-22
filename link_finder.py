from page_parser import PageParser
from urllib import parse

class LinkFinder(PageParser):
    def __init__(self, base_url, page_url):
        super().__init__(base_url, page_url);
        self.links = set();
        self.tag_handlers['a'] = self.tag_handler;
    
    def tag_handler(self, tag, attrs):
        if tag == 'a':
            for (attribute, value) in attrs:
                if attribute == 'href':
                    url = parse.urljoin(self.base_url, value)
                    self.links.add(url);

    def page_links(self):
        return self.links;

    def error(self, message):
      pass