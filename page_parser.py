from html.parser import HTMLParser
import urllib
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
    def __init__(self, base_url, page_url, white_list = None, target_definition = None, data_storage_path = './'):
        super().__init__();
        self.base_url = base_url;
        self.page_url = page_url;
        self.tag_handlers = dict();
        self.tag_stack = [];
        self.__components = [];
        self.__links = set();
        self.white_list = [];
        if not white_list is None:
            self.white_list = white_list;

        self.targets = [];
        if not target_definition is None:
            for target_def in target_definition:
                t = Target(base_url, target_def, data_storage_path, page_url);
                if t.is_page_a_target(self.page_url):
                    self.targets.append(t);

        self.selector_path_count = {};


    def current_selector(self, tags = None, return_text=False, use_nth_child=False):
        tag_stack = tags;
        if tags is None:
            tag_stack = self.tag_stack;

        selector_path = [];

        if len(tag_stack) != 0:
            for t in tag_stack:
                ts = None;
                if use_nth_child:
                    ts = t.selector();
                else:
                    ts = t.selector_without_nth_child();

                if t.is_using_id():
                    selector_path = [ts];
                else:
                    selector_path.append(ts);

            if len(selector_path) >= 1 \
               and Target.is_selector_match(selector_path[0], 'html'):
               selector_path = selector_path[1:];

        if return_text:
            return ' > '.join(selector_path);
        else:
            return selector_path;


    def is_link_in_white_list(self, url):
        if len(self.white_list) == 0:
            return True;
        else:
            o = urllib.parse.urlparse(url);
            if o.netloc in self.white_list \
            or o.scheme + '://' + o.netloc in self.white_list:
                return True;
            else:
                return False;

    # When we call HTMLParser feed() this function is called when it encounters an opening tag <a>
    def handle_starttag(self, tag, attrs):
        t = HtmlTag(tag, attrs);
        if len(self.tag_stack) > 0:
            self.tag_stack[-1].addSubTag(t);

        self.tag_stack.append(t);

        # count the children index
        current_selector_path = self.current_selector(return_text = True, use_nth_child = False);
        if current_selector_path not in self.selector_path_count:
            self.selector_path_count[current_selector_path] = t;
        else:
            previous_value = self.selector_path_count[current_selector_path];
            nth_child = 1;
            if type(previous_value) == HtmlTag:
                previous_value.nth_child = nth_child;
            elif type(previous_value) == int:
                nth_child = previous_value;
            nth_child += 1;
            self.selector_path_count[current_selector_path] = nth_child;
            t.nth_child = nth_child;

        # Gather links
        if tag == 'a':
            for (attribute, value) in attrs:
                if attribute == 'href':
                    url = urllib.parse.urljoin(self.base_url, value);
                    if self.is_link_in_white_list(url):
                        self.__links.add(url);


    def page_links(self):
        return self.__links;


    def pop_tag_stack(self):
        if len(self.targets) > 0:
            current_selector_path = self.current_selector(self.tag_stack, use_nth_child = True);
            for target_inst in self.targets:
                target_inst.process(current_selector_path, self.tag_stack[-1]);
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