from content_extractor.html_tag import HtmlTag
from content_extractor.selector_node import SelectorNode
from content_extractor.selector_search_tree_component import Component
from content_extractor.selector_search_tree_node import SelectorSearchTreeNode
from content_extractor.storage import StorageWrapper
import urllib
import re
import json
from threading import Lock;

class ContentTarget:

    def __init__(self, base_url, target_def, storage_base_path):
        self.component_search_tree = SelectorSearchTreeNode();
        self.base_url = base_url;
        self.content = {};
        self.mutex = Lock();
        self.set_target(target_def, storage_base_path);

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

        self.ignore_ids = [];
        if 'ignore_ids' in target_def:
            self.ignore_ids = target_def['ignore_ids'];

        storage_def = None;
        if 'storage' in target_def:
            storage_def = target_def['storage'];
        self.storage = StorageWrapper(storage_base_path, storage_def, self.name);

    def ignore_id_in_tag(self, tag):
        if tag is None:
            return False;

        if len(self.ignore_ids) == 0:
            return False;

        tag_id = tag.id();
        if tag_id is None:
            return False;

        if tag_id in self.ignore_ids:
            tag.remove_id();
            return True;
        else:
            for item in self.ignore_ids:
                if '\\' in item:
                    if re.match(item, tag_id) is not None:
                        tag.remove_id();
                        return True;

        return False;


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
                    if '\\' in su or '.*' in su or '.+' in su or '?' in su:
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

        if type(comp) != Component:
            idx = 0;
            for t in ['columns', 'sub_components']:
                if t in comp:
                    for sub_def in comp[t]:
                        sub_comp = Component(sub_def, idx);
                        comp_inst.add_sub_component(sub_comp);
                        self.add_component(sub_comp);
                        idx += 1;


    def search_component_by_selector(self, selector_path_or_list):
        selector_list = selector_path_or_list;
        if type(selector_path_or_list) == str:
            selector_list = selector_path_or_list.split(' > ');

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


    def process_tag(self, page_url, selector_path, html_container):
        (comp_inst, comp_content) = self.gather_content(selector_path, html_container, page_url);
        if comp_inst is not None:
            self.mutex.acquire();
            if page_url not in self.content:
                self.content[page_url] = {};
            self.mutex.release();

            content = self.content[page_url];
            if comp_inst.parent is None:
                content[comp_inst.role] = comp_content;
            else:
                # Create path for that component
                path = [];
                tmp_inst = comp_inst;
                while tmp_inst.parent is not None:
                    tmp_inst = tmp_inst.parent;
                    path.append(tmp_inst);
                pointer = content;
                for i in range(len(path)-1, -1, -1):
                    tmp_inst = path[i];
                    if tmp_inst.role not in pointer:
                        pointer[tmp_inst.role] = {};
                        pointer = pointer[tmp_inst.role];
                    elif i != len(path)-1 and tmp_inst.index > 0:
                        if type(pointer[tmp_inst.role]) != list:
                            pointer[tmp_inst.role] = [pointer[tmp_inst.role]];
                        while tmp_inst.index >= len(pointer[tmp_inst.role]):
                            pointer[tmp_inst.role].append({});
                        pointer = pointer[tmp_inst.role][tmp_inst.index];
                # Now pointer is the very parent of comp_inst
                if comp_inst.role not in pointer:
                    pointer[comp_inst.role] = comp_content;
                else:
                    if type(pointer[comp_inst.role]) != list:
                        pointer[comp_inst.role] = [pointer[comp_inst.role]];
                    pointer[comp_inst.role].append(comp_content);

        

    def gather_content(self, selector_path, html_container, page_url):
        selector_list = selector_path;
        if type(selector_path) == str:
            selector_list = selector_path.split(' > ');

        result = '';

        comp = self.search_component_by_selector(selector_list);

        if comp is None:
            return (comp, result);

        # Found the target component in the search tree, and store the content
        component_url = None;
        component_text = html_container.text().strip();

        if comp.format == 'image':
            if comp.content_property is not None and comp.content_property in html_container.attrs:
                component_url = urllib.parse.urljoin(self.base_url, html_container.attrs[comp.content_property]);
            elif html_container.tag == 'img' and 'src' in html_container.attrs:
                component_url = urllib.parse.urljoin(self.base_url, html_container.attrs['src']);
            elif html_container.tag == 'a' and 'href' in html_container.attrs:
                component_url = urllib.parse.urljoin(self.base_url, html_container.attrs['href']);
        elif comp.content_property is not None:
            p = comp.content_property;
            if p in html_container.attrs:
                component_text = html_container.attrs[p].strip();


        # filter out the CDN syntax
        if comp.format == 'image' and component_url is not None\
        and '@' in component_url:
            component_url = '@'.join(component_url.split('@')[:-1]);

        # process the content of single item:
        if comp.format == 'image':
            # Store the image in current page directory with a hash name
            print('retrieving resource:', component_url);
            result = component_url;
            result = self.storage.store_resource(component_url, comp.format, page_url);
            
        elif comp.format == 'text':
            result = component_text;
        elif comp.format == 'json':
            try:
                result = json.loads(component_text, strict=False);
            except Exception as e:
                print('ERROR when parsing component [', comp.role, comp.format, ']', str(e));
            else:
                pass
            finally:
                pass
        else:
            pass;

        return (comp, result);


    def end_page(self, page_url):
        self.mutex.acquire();
        file_path = None;
        try:
            file_path = self.storage.store_page(self.content[page_url], page_url);
            del self.content[page_url];
        except Exception as e:
            print('ERROR when storing page:', page_url, ', error message:', str(e));
            pass
        finally:
            # pass;
            self.mutex.release();

        return file_path;

    def end_spider(self):
        self.storage.save_meta();



