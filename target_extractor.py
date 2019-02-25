from html_tag import HtmlTag
import re

class Component:

    def __init__(self, comp_def):
        self.role = comp_def['role'];
        self.format = comp_def['format'];
        self.preprocess = {};
        if 'preprocess' in comp_def:
            self.preprocess = comp_def['preprocess'];
        self.selector = comp_def['selector'];


class Target:

    def __init__(self, target_def):
        self.component_search_tree = {
            'component': None,
            'children': {}
        };

        self.set_target(target_def);


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
            for comp_def in target_def['components']:
                self.add_component(comp_def);


    def normalize_selector(self, selector):
        s = re.sub(r':?.?nth-child\(\d+\)', '', selector);
        return s;

    # classes of target could be less than instance, 
    # such as, for some place in page the tag could be 'div.main-content.w1240'
    # but in the definition, we can only us 'dev.main-content'
    # because the class 'w.1240' is responsive design element and does not matter
    # in this situation, they are matched
    def is_selector_match(self, sel_target, sel_inst):
        if sel_inst[0] == '#':
            return sel_inst == sel_target;
        else:
            target = self.normalize_selector(sel_target).split('.');
            inst = sel_inst.split('.');
            if target[0] != inst[0] or len(inst) > len(target):
                return False;
            elif len(inst) == 0 and len(target) == 0:
                return True;
            else:
                for i in inst:
                    if not i in target:
                        return False;
                return True;                


    def selector_in_dict(self, selector_inst, comp_dict):
        for key in comp_dict:
            if self.is_selector_match(key, selector_inst):
                return key;
        return None;


    def add_component(self, comp, is_inst = False):
        comp_inst = comp;
        if not is_inst:
            comp_inst = Component(comp);

        pointer = self.component_search_tree;
        for s in comp_inst.selector.split(' > '):
            if s not in pointer['children']:
                pointer['children'][s] = {
                    'component': None,
                    'children': {}
                };
            pointer = pointer['children'][s];
        pointer['component'] = comp_inst;


    def search_component_by_selector(self, selector_path, is_text = False):
        selector_list = selector_path;
        if is_text:
            selector_list = selector_path.split(' > ');

        pointer = self.component_search_tree;
        for selector in selector_list:
            key = self.selector_in_dict(selector, pointer['children']);
            if not key is None:
                pointer = pointer['children'][key];
            else:
                return None;
        return pointer['component'];