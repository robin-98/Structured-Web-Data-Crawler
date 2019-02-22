from html.parser import HTMLParser
from urllib import parse


class PageParser(HTMLParser):

  def __init__(self, base_url, page_url):
    super().__init__();
    self.base_url = base_url;
    self.page_url = page_url;
    self.extra_tag_handlers = dict();
    print('page parser base url:', self.base_url, 'page url:', self.page_url)

    # When we call HTMLParser feed() this function is called when it encounters an opening tag <a>
    def handle_starttag(self, tag, attrs):
      print('tag:', tag, 'attrs:', attr);
      # if tag in self.tag_handlers:
      #   handler = self.extra_tag_handlers[tag];
      #   print('base class preparing to invoke tag handler');
      #   print('tag:', tag,'handler:', handler);
      #   handler(tag, attrs);

    def error(self, message):
      pass