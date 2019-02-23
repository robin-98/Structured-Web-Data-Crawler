from html.parser import HTMLParser
from urllib import parse

class HtmlTag:

    def __init__(self, tagStr, attrs):
        self.tag = tagStr;
        self.attrs = attrs;

        # array of contents contain tags and paragraphs of text
        self.contents = []; 

    def addSubTag(self, tagInst):
        self.contents.append(tagInst);


    def addText(self, text):
        self.contents.append(text);


    def text(self):
        content = '';
        for c in self.contents:
            if isinstance(c, HtmlTag):
                content += c.text();
            elif isinstance(c, str):
                content += c;

        return content;


# class Link:

#     def __init__(self, url, text):
#         self.url = url;
#         self.text = text;




class PageParser(HTMLParser):

    def __init__(self, base_url, page_url):
        super().__init__();
        self.base_url = base_url;
        self.page_url = page_url;
        self.tag_handlers = dict();
        self.tag_stack = [];
        self.__components = [];
        self.__links = set();
    

    # When we call HTMLParser feed() this function is called when it encounters an opening tag <a>
    def handle_starttag(self, tag, attrs):
        # if tag in self.tag_handlers:
        #     handler = self.tag_handlers[tag];
        #     handler(tag, attrs);
        t = HtmlTag(tag, attrs);
        if len(self.tag_stack) > 0:
            self.tag_stack[-1].addSubTag(t);

        self.tag_stack.append(t);

        # Gather links
        if tag == 'a':
            for (attribute, value) in attrs:
                if attribute == 'href':
                    url = parse.urljoin(self.base_url, value)
                    self.__links.add(url);


    def page_links(self):
        return self.__links;

    
    def handle_endtag(self, tag):
        if len(self.tag_stack) == 0:
            return;

        t = self.tag_stack.pop();
        while len(self.tag_stack) > 0 and t.tag != tag:
            t = self.tag_stack.pop();

        if len(self.tag_stack) == 0:
            self.__components.append(t);

    
    def handle_data(self, data):
        if len(self.tag_stack) > 0:
            self.tag_stack[-1].addText(data);


    def components(self):
        return self.__components;


    def text(self):
        return ''.join([c.text() for c in self.__components]);
    

    def error(self, message):
        pass;