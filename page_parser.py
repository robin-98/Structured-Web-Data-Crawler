from html.parser import HTMLParser
from urllib import parse
from html_tag import HtmlTag
from target_extractor import Target
# Link structure is yet NOT supportable
# class Link:
#     '''Link instance inside a webpage,
#        to record its parent links and link texts
#     '''
#     def __init__(self, url, text):
#         self.url = url;
#         self.texts = set();
#         if not text is None:
#             self.texts[text] = True;

#         self.parent_links = {};

#     def addParentLink(self, url, text):
#         if not url in self.parent_links:
#             p = Link(url, text);
#             self.parent_links[url] = p;
#         else:
#             p = self.parent_links[url];
#             if not text in p.texts:
#                 p.texts.add(text);

#     def link_texts(self):
#         return list(self.texts);


class PageParser(HTMLParser):
    '''Inherit from HtmlParser
        maintaining an inner stack instance to track
        the document structure and the tag container path
    '''
    def __init__(self, base_url, page_url, target_definition = None):
        super().__init__();
        self.base_url = base_url;
        self.page_url = page_url;
        self.tag_handlers = dict();
        self.tag_stack = [];
        self.__components = [];
        self.__links = set();
        self.targets = [];
        if not target_definition is None:
            for target_def in target_definition:
                self.targets.append(Target(target_def));


    def current_selector(self, return_text=False):
        if len(self.tag_stack) == 0:
            return '';

        selector = [];
        for t in self.tag_stack:
            if t.is_using_id():
                selector = [t.selector()];
            else:
                selector.append(t.selector());

        if return_text:
            return ' > '.join(selector);
        else:
            return selector;


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

        current_selector = self.current_selector();
        for t in self.targets:
            comp = t.search_component_by_selector(current_selector);
            if not comp is None:
                print('*'*30);
                print('* ', current_selector(return_text = True));
                print('*'*30);


    
    def handle_data(self, data):
        if len(self.tag_stack) > 0:
            self.tag_stack[-1].addText(data);


    def components(self):
        return self.__components;


    def text(self):
        return ''.join([c.text() for c in self.__components]);
    

    def error(self, message):
        pass;