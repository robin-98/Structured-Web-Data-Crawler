from html.parser import HTMLParser
import urllib
from content_extractor.html_tag import HtmlTag


from content_extractor.content_target import ContentTarget
from content_extractor.selector_node import SelectorNode


class PageParser(HTMLParser):
    '''Inherit from HtmlParser
        maintaining an inner stack instance to track
        the document structure and the tag container path
    '''
    def __init__(self, base_url, page_url, white_list = None):
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
        
        self.selector_path_count = {};

    def add_targets(self, content_target_insts):
        if type(content_target_insts) != list:
            return;
        for t in content_target_insts:
            self.add_target(t);

    def add_target(self, content_target_inst):
        if content_target_inst is None or type(content_target_inst) != ContentTarget:
            return;
        if content_target_inst.is_page_a_target(self.page_url):
            self.targets.append(content_target_inst);


    def current_selector(self, tags = None, return_text=False, use_nth_child=False, only_use_nth_child=False):
        tag_stack = tags;
        if tags is None:
            tag_stack = self.tag_stack;

        selector_path = [];

        if len(tag_stack) != 0:
            for t in tag_stack:
                ts = None;
                if use_nth_child:
                    ts = t.selector();
                elif only_use_nth_child:
                    ts = t.selector_only_nth_child();
                else:
                    ts = t.selector_without_nth_child();

                if t.is_using_id():
                    selector_path = [ts];
                else:
                    selector_path.append(ts);

            if len(selector_path) > 0 \
               and SelectorNode('html').match(selector_path[0]):
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
            # close those incorrectlly defined meta and link tags
            parallelable_tags = ['meta', 'link'];
            if self.tag_stack[-1].tag in parallelable_tags:
                self.handle_endtag(self.tag_stack[-1].tag);
            else:
                self.tag_stack[-1].addSubTag(t);

        self.tag_stack.append(t);

        # count the children index
        current_selector_path = self.current_selector(return_text = True, only_use_nth_child = True);
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
                target_inst.process_tag(self.page_url, current_selector_path, self.tag_stack[-1]);
        return self.tag_stack.pop();

    
    def handle_endtag(self, tag):
        if len(self.tag_stack) == 0:
            return;

        t = self.pop_tag_stack();
        while len(self.tag_stack) > 0 and t.tag != tag:
            t = self.pop_tag_stack();

        if len(self.tag_stack) == 0:
            self.__components.append(t);

        if tag == 'html':
            for target_inst in self.targets:
                file_path = target_inst.end_page(self.page_url);
                if file_path is not None:
                    print('[' + target_inst.name +']', 'is stored in file: [' + file_path + '] for page: [' + self.page_url + ']');
        

    
    def handle_data(self, data):
        if len(self.tag_stack) > 0:
            self.tag_stack[-1].addText(data);


    def components(self):
        return self.__components;


    def text(self):
        return ''.join([c.text() for c in self.__components]);
    

    def error(self, message):
        pass;