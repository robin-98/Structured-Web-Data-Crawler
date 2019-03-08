from content_extractor.html_tag import HtmlTag
from content_extractor.selector_node import SelectorNode
from content_extractor.selector_search_tree_component import Component
from content_extractor.selector_search_tree_node import SelectorSearchTreeNode
from content_extractor.storage import StorageWrapper
import urllib
import re


class ContentTarget:

    def __init__(self, base_url, target_def, storage_base_path, page_url):
        self.component_search_tree = SelectorSearchTreeNode();
        self.set_target(target_def, storage_base_path);
        self.base_url = base_url;
        self.page_url = page_url;

    def set_target(self, target_def, storage_base_path):
        self.name = target_def['name'];
        self.sub_domains = set();
        if 'sub_domains' in target_def:
            for s in target_def['sub_domains']:
                self.sub_domains.add(s);
        self.sub_urls = set();
        if 'sub_urls' in target_def:
            for u in target_def['sub_urls']:
                self.sub_urls.add(u);

        if 'components' in target_def:
            comp_idx = 0;
            for comp_def in target_def['components']:
                self.add_component(comp_def, comp_idx);
                comp_idx += 1;


        storage_def = None;
        if 'storage' in target_def:
            storage_def = target_def['storage'];
        self.storage = StorageWrapper(storage_base_path, storage_def);



    def is_page_a_target(self, page_url):
        o = urllib.parse.urlparse(page_url);

        if len(self.sub_domains) == 0 \
        or o.netloc in self.sub_domains \
        or o.scheme + '://' + o.netloc in self.sub_domains:
            if len(self.sub_urls) == 0:
                return True;
            else:
                for su in self.sub_urls:
                    # if sub url is matched exactly as head substring
                    if su in o.path \
                    and o.path.index(su) == 0:
                        return True;
                    # if sub url is a regex string
                    if '\\' in su:
                        if re.match(su, o.path) is not None:
                            return True;
        return False;


    def add_component(self, comp, comp_idx = 0):
        comp_inst = comp;
        if type(comp) != Component:
            comp_inst = Component(comp, comp_idx);

        pointer = self.component_search_tree;
        for s in comp_inst.selector.split(' > '):
            if s not in pointer.children:
                pointer.children[s] = SelectorSearchTreeNode(selector_node = SelectorNode(s));
            pointer = pointer.children[s];
        pointer.component = comp_inst;

        for sub_comp in comp_inst.sub_components:
            self.add_component(sub_comp);

    def search_component_by_selector(self, selector_path_or_list):
        
        selector_list = selector_path_or_list;
        if type(selector_path_or_list) == str:
            selector_list = selector_path_or_list.split(' > ');

        # DEBUG
        # print('searching', ' > '.join(selector_list));
        # is_debugging = False;
        # if len(selector_list) > 2 and selector_list[0] == 'body' \
        # and re.match(r'div.*\.cover.*', selector_list[-2]) is not None \
        # and re.match(r'img.*', selector_list[-1]) is not None:
        #     is_debugging = True;
        #     print('searching', ' > '.join(selector_list));
        # END OF DEBUG

        pointer = self.component_search_tree;
        for selector in selector_list:
            key = None;
            for k in pointer.children:
                selector_node = pointer.children[k].selector_node;
                if selector_node.match(selector):
                    key = k;
                    break;

            if key is not None:
                pointer = pointer.children[key];
            else:
                return None;
        # DEBUG
        # if is_debugging and pointer.component is not None:
        #     print('found', pointer.component.role, pointer.component.format)
        # END OF DEBUG

        return pointer.component;


    def process(self, selector_path, html_container):
        self.gather_content(selector_path, html_container);
        

    def gather_content(self, selector_path, html_container):
        selector_list = selector_path;
        if type(selector_path) == str:
            selector_list = selector_path.split(' > ');

        comp = self.search_component_by_selector(selector_list);

        # DEBUG
        # print('search selector instance in component tree:', ' > '.join(selector_list));

        # if len(selector_list) > 1 and selector_list[0] == 'head':
        #     print('searching', ' > '.join(selector_list));

        # if comp is not None:
        #     print(' > '.join(selector_list), 'is found');
        # END OF DEBUG

        if comp is None:
            return;

        if len(comp.sub_components) > 0:
            # print(html_container.sub_tags());
            # for sub_comp in comp.sub_components:
            # Each element in the html_container should be examed to know whether it is a target component and write down its content with its index
            for s in html_container.all_sub_selectors():
                parts = s['selector'].split(' > ');
                if len(parts) < 2:
                    continue;
                sub_selector = comp.selector + ' > ' + ' > '.join(parts[1:]);
                self.gather_content(sub_selector, s['tag']);

        else:
            # DEBUG MULTI SUB COMPONENT
            # return;
            # END OF DEBUG

            # Found the target component in the search tree, and store the content
            component_url = None;
            component_text = html_container.text().strip();
            if comp.content_property is not None:
                p = comp.content_property;
                if p in html_container.attrs:
                    component_text = html_container.attrs[p].strip();

            if len(component_text) == 0:
                component_text = None;

            if comp.format == 'image':
                if html_container.tag == 'img' and 'src' in html_container.attrs:
                    component_url = urllib.parse.urljoin(self.base_url, html_container.attrs['src']);
                elif html_container.tag == 'a' and 'href' in html_container.attrs:
                    component_url = urllib.parse.urljoin(self.base_url, html_container.attrs['href']);

            # filter out the CDN syntax
            if component_url is not None and '@' in component_url:
                component_url = '@'.join(component_url.split('@')[:-1]);
            comp_desc = 'No. ' + str(comp.index) + ' ' + comp.role + ' [' + comp.format + '] ' + 'in tag <' + html_container.tag +'> in page ' + self.page_url;
            print('===> storing', comp_desc);
            self.storage.store_component_naively(self.page_url, self.name, comp, component_url, component_text);
            print('<=== stored', comp_desc)


    



