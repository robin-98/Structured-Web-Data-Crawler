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


    def current_selector(self, tags = None, return_text=False):
        tag_stack = tags;
        if tags is None:
            tag_stack = self.tag_stack;

        selector_path = [];

        if len(tag_stack) != 0:
            for t in tag_stack:
                if t.is_using_id():
                    selector_path = [t.selector()];
                else:
                    selector_path.append(t.selector());

            if len(selector_path) >= 1 \
               and Target.is_selector_match(selector_path[0], 'html'):
               selector_path = selector_path[1:];

        if return_text:
            return ' > '.join(selector_path);
        else:
            return selector_path;


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


    def pop_tag_stack(self):
        current_selector = self.current_selector(self.tag_stack);
        print('current selector:', current_selector);
        for target_inst in self.targets:
            comp = target_inst.search_component_by_selector(current_selector);
            if not comp is None:
                ################################
                ### Process the target component
                print('*'*50);
                print(self.tag_stack[-1].text());
                print('*'*50);
                ################################

        return self.tag_stack.pop();

    
    def handle_endtag(self, tag):
        if len(self.tag_stack) == 0:
            return;

        t = self.pop_tag_stack();
        while len(self.tag_stack) > 0 and t.tag != tag:
            t = self.pop_tag_stack();

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