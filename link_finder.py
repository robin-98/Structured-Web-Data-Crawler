from page_parser import PageParser
from urllib import parse


class LinkFinder(PageParser):

    def __init__(self, base_url, page_url):
        super().__init__(base_url, page_url);
        self.links = set()
        # self.extra_tag_handlers['a'] = self.tag_handler;
        print('link finder base url:', self.base_url, 'page url:', self.page_url);

    # When we call HTMLParser feed() this function is called when it encounters an opening tag <a>
    def tag_handler(self, tag, attrs):
        print('invoking link_tag_handle, tag:', tag, 'attrs:', attrs);
        for (attribute, value) in attrs:
            if attribute == 'href':
                url = parse.urljoin(self.base_url, value)
                self.links.add(url)
            

    def page_links(self):
        return self.links

    def error(self, message):
        pass
