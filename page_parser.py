from html.parser import HTMLParser
from urllib import parse


class PageParser(HTMLParser):

    def __init__(self, base_url, page_url):
        super().__init__();
        self.base_url = base_url;
        self.page_url = page_url;
        self.tag_handlers = dict();

    # When we call HTMLParser feed() this function is called when it encounters an opening tag <a>
    def handle_starttag(self, tag, attrs):
        if tag in self.tag_handlers:
            handler = self.tag_handlers[tag];
            handler(tag, attrs);

    def error(self, message):
        pass