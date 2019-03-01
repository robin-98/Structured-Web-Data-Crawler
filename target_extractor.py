from html_tag import HtmlTag
import urllib
import re
import hashlib
import os

class SelectorNode:

    def __init__(self, selector_str):
        self.selector = selector_str;
        (self.tag, self.classes, self.constraints) = SelectorNode.parse_selector(selector_str);
        

    @staticmethod
    def parse_selector(selector_str):
        tag = selector_str;
        constraints = [];
        if ':' in selector_str:
            parts = selector_str.split(':');
            tag = parts[0];
            for c in parts[1:]:
                constraints.append(SelectorNode.parse_constraint(c));
        classes = set();
        if '.' in tag:
            parts = tag.split('.');
            tag = parts[0];
            for c in parts[1:]:
                classes.add(c);
        return (tag, classes, constraints);

    @staticmethod
    def parse_constraint(constraint_str):
        (constraint_type, constraint_value) = (None, None);
        if '=' in constraint_str:
            parts = constraint_str.split('=');
            constraint_type = parts[0];
            constraint_value = '='.join(parts[1:]);
        elif 'nth-child' in constraint_str:
            values = re.findall(r'\d+', constraint_str);
            if len(values) > 0:
                constraint_type = 'nth-child';
                constraint_value = values[0];
        return (constraint_type, constraint_value);


    def match(self, selector_instance):
        # First, check the selector by its id, and other situations if they match literally
        if selector_instance == self.selector:
            return True;


        (tag, classes, constraints) = SelectorNode.parse_selector(selector_instance);
        # For other situations which do not require element id,
        # the tag should be checked at first
        if tag != self.tag:
            return False;

        # Then their classes should be checked before checking any constraints
        # classes of component definition could be less than instance, 
        # such as, for some place in page the tag could be 'div.main-content.w1240'
        # but in the definition, we can only us 'dev.main-content'
        # because the class 'w.1240' is responsive design element which could change
        # which means every class in the component definition should match in the instance
        for c in self.classes:
            if c not in classes:
                return False;

        # Third, check the selector by its constraints
        # every constraint in the component definition should match in the instance
        for (c_def_type, c_def_value) in self.constraints:
            is_matched_in_instance = False;
            c_inst_nth_child = 0;
            for (c_inst_type, c_inst_value) in constraints:
                if c_inst_type == 'nth-child':
                    c_inst_nth_child = c_inst_value;
                if c_inst_type == c_def_type and c_inst_value == c_def_value:
                    is_matched_in_instance = True;
                    break;
            if not is_matched_in_instance\
            and c_def_type == 'nth-child'\
            and c_def_value == 1\
            and c_inst_nth_child == 0:
                is_matched_in_instance = True;

            if not is_matched_in_instance:
                return False;

        # If can NOT find and violation, which means the instance matches all constraints
        return True;


class Component:

    def __init__(self, comp_def, comp_idx):
        self.role = comp_def['role'];
        self.format = comp_def['format'];
        self.selector = comp_def['selector'];
        self.index = comp_idx;


class Target:

    def __init__(self, base_url, target_def, storage_base_path, page_url):
        self.component_search_tree = {
            'component': None,
            'selector_node': None,
            'children': {}
        };
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
                    if su in o.path \
                    and o.path.index(su) == 0:
                        return True;
        return False;


    def add_component(self, comp, comp_idx = 0, is_inst = False):
        comp_inst = comp;
        if not is_inst:
            comp_inst = Component(comp, comp_idx);

        pointer = self.component_search_tree;
        for s in comp_inst.selector.split(' > '):
            if s not in pointer['children']:
                pointer['children'][s] = {
                    'component': None,
                    'selector_node': SelectorNode(s),
                    'children': {}
                };
            pointer = pointer['children'][s];
        pointer['component'] = comp_inst;


    def search_component_by_selector(self, selector_list):
        # print('checking path:', ' > '.join(selector_list));
        pointer = self.component_search_tree;
        for selector in selector_list:
            key = None;
            for k in pointer['children']:
                selector_node = pointer['children'][k]['selector_node'];
                if selector_node.match(selector):
                    key = k;
                    break;

            if key is not None:
                pointer = pointer['children'][key];
            else:
                return None;
        search_result = pointer['component'];
        # if search_result is not None:
            # print('matched in search tree')

        return search_result;


    @staticmethod
    def hash_path(base_path, sub_path):
        hash_sub_path = hashlib.sha256(sub_path.encode('utf-8')).hexdigest();
        return urllib.parse.urljoin(base_path + '/', './' + hash_sub_path);


    def process(self, selector_path, html_container):
        selector_list = selector_path;
        if type(selector_path) == str:
            selector_list = selector_path.split(' > ');

        comp = self.search_component_by_selector(selector_list);
        if comp is None:
            return;

        # Found the target component in the search tree, and store the content
        component_url = None;
        component_text = html_container.text().strip();

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
            self.storage_path = Target.hash_path(urllib.parse.urljoin(self.storage_base_path + '/', './' + self.name), self.page_url);
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



