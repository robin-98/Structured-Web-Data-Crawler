from html_tag import HtmlTag
import urllib
import re
import hashlib
import os

class Component:

    def __init__(self, comp_def, comp_idx):
        self.role = comp_def['role'];
        self.format = comp_def['format'];
        self.preprocess = {};
        if 'preprocess' in comp_def:
            self.preprocess = comp_def['preprocess'];
        self.selector = comp_def['selector'];
        self.index = comp_idx;


class Target:

    def __init__(self, base_url, target_def, storage_base_path, page_url):
        self.component_search_tree = {
            'component': None,
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


    @staticmethod
    def normalize_selector(selector):
        s = re.sub(r':?.?nth-child\(\d+\)', '', selector);
        return s;

    # classes of target could be less than instance, 
    # such as, for some place in page the tag could be 'div.main-content.w1240'
    # but in the definition, we can only us 'dev.main-content'
    # because the class 'w.1240' is responsive design element and does not matter
    # in this situation, they are matched
    @staticmethod
    def is_selector_match(sel_inst, sel_target):
        if sel_inst[0] == '#':
            return sel_inst == sel_target;
        else:
            target = Target.normalize_selector(sel_target).split('.');
            inst = sel_inst.split('.');
            if target[0] != inst[0] or len(inst) < len(target):
                return False;
            elif len(inst) == 0 and len(target) == 0:
                return True;
            else:
                for t in target:
                    if not t in inst:
                        return False;
                return True;                

    @staticmethod
    def selector_in_dict(selector_inst, comp_dict):
        for key in comp_dict:
            if Target.is_selector_match(selector_inst, key):
                return key;
        return None;


    def add_component(self, comp, comp_idx = 0, is_inst = False):
        comp_inst = comp;
        if not is_inst:
            comp_inst = Component(comp, comp_idx);

        pointer = self.component_search_tree;
        for s in comp_inst.selector.split(' > '):
            if s not in pointer['children']:
                pointer['children'][s] = {
                    'component': None,
                    'children': {}
                };
            pointer = pointer['children'][s];
        pointer['component'] = comp_inst;


    def search_component_by_selector(self, selector_list):
        pointer = self.component_search_tree;
        for selector in selector_list:
            key = Target.selector_in_dict(selector, pointer['children']);
            if not key is None:
                pointer = pointer['children'][key];
            else:
                return None;
        search_result = pointer['component'];

        return search_result;


    @staticmethod
    def hash_path(base_path, sub_path):
        hash_sub_path = hashlib.sha256(sub_path.encode('utf-8')).hexdigest();
        return urllib.parse.urljoin(base_path + '/', './' + hash_sub_path);


    def process(self, selector_path, html_container, is_text = False):
        selector_list = selector_path;
        if is_text:
            selector_list = selector_path.split(' > ');

        comp = self.search_component_by_selector(selector_path);
        if comp is None:
            return;

        component_url = None;
        component_text = html_container.text().strip();

        if len(component_text) == 0:
            component_text = None;

        if comp.format == 'image' and html_container.tag == 'img' and 'src' in html_container.attrs:
            component_url = urllib.parse.urljoin(self.base_url, html_container.attrs['src']);
        
        comp_desc = 'No. ' + str(comp.index) + ' ' + comp.role + ' [' + comp.format + '] ' + 'in tag <' + html_container.tag +'>'
        print('===> storing', comp_desc);
        self.store_component(comp, component_url, component_text);
        print('<=== stored', comp_desc)



    def store_component(self, component_instance, component_url = None, component_text = None):
        if self.storage_path is None:
            self.storage_path = Target.hash_path(self.storage_base_path, self.page_url);
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
            data_file_name = self.storage_path + '/' + file_base_name + '.txt';
            print('data file:', data_file_name);
            with open(data_file_name, 'w') as f:
                f.write(component_text);






