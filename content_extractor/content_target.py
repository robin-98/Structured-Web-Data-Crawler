from content_extractor.html_tag import HtmlTag
from content_extractor.selector_node import SelectorNode
from content_extractor.selector_search_tree_component import Component
from content_extractor.selector_search_tree_node import SelectorSearchTreeNode
import urllib
import re
import hashlib
import os


class ContentTarget:

    def __init__(self, base_url, target_def, storage_base_path, page_url):
        self.component_search_tree = SelectorSearchTreeNode();
        self.set_target(target_def);
        self.storage_base_path = storage_base_path;
        self.base_url = base_url;
        self.page_url = page_url;
        self.storage_path = None;


    def set_target(self, target_def):
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


    def add_component(self, comp, comp_idx = 0, is_inst = False):
        comp_inst = comp;
        if not is_inst:
            comp_inst = Component(comp, comp_idx);

        pointer = self.component_search_tree;
        for s in comp_inst.selector.split(' > '):
            if s not in pointer.children:
                pointer.children[s] = SelectorSearchTreeNode(selector_node = SelectorNode(s));
            pointer = pointer.children[s];
        pointer.component = comp_inst;


    def search_component_by_selector(self, selector_list):
        # DEBUG
        # if len(selector_list) > 2 and selector_list[0] == 'body' \
        # and re.match(r'div.*\.cover.*', selector_list[-2]) is not None \
        # and re.match(r'img.*', selector_list[-1]) is not None:
        #      print('searching', ' > '.join(selector_list));
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

        return pointer.component;


    @staticmethod
    def hash_path(base_path, sub_path):
        hash_sub_path = hashlib.sha256(sub_path.encode('utf-8')).hexdigest();
        return urllib.parse.urljoin(base_path + '/', './' + hash_sub_path);


    def process(self, selector_path, html_container):
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
            # for s in html_container.all_sub_selectors():
            #     print(s);

        else:
            # DEBUG MULTI SUB COMPONENT
            return;
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
            self.store_component(comp, component_url, component_text);
            print('<=== stored', comp_desc)


    def store_component(self, component_instance, component_url = None, component_text = None):
        if self.storage_path is None:
            self.storage_path = ContentTarget.hash_path(urllib.parse.urljoin(self.storage_base_path + '/', './' + self.name), self.page_url);
            if not os.path.exists(self.storage_path):
                os.makedirs(self.storage_path);
            # store meta data
            with open(self.storage_path + '/meta.txt', 'w') as f:
                f.write('page_url: ' + self.page_url);

        file_base_name = component_instance.role + '_' + str(component_instance.index);
        file_name = file_base_name;
        if component_url is not None:
            o = urllib.parse.urlparse(component_url);
            if component_instance.format == 'image':
                file_name += '_' + o.path.split('/')[-1];
            elif component_instance.format == 'text':
                file_name += '_raw.txt';
            
            data_file_name = self.storage_path + '/' + file_name;
            print('data file:', data_file_name);
            urllib.request.urlretrieve(component_url, data_file_name);
        
        if component_text is not None:
            surfix = '.txt';
            if component_instance.format == 'json':
                surfix = '.json';
            data_file_name = self.storage_path + '/' + file_base_name + surfix;
            print('data file:', data_file_name);
            with open(data_file_name, 'w') as f:
                f.write(component_text);



