class Component:

    def __init__(self, comp_def, comp_idx):
        self.role = None;
        if 'role' in comp_def:
            self.role = comp_def['role'];
        elif 'name' in comp_def:
            self.role = comp_def['name'];

        self.format = 'text';
        if 'format' in comp_def:
            self.format = comp_def['format'];

        self.selector = None;
        if 'selector' in comp_def:
            self.selector = comp_def['selector'];

        self.index = comp_idx;
        
        self.content_property = None;
        if 'content_property' in comp_def:
            self.content_property = comp_def['content_property'];

        self.sub_selector = None;
        if 'sub_selector' in comp_def:
            self.sub_selector = comp_def['sub_selector'];

        self.parent = None;

    def add_sub_component(self, sub_comp):
        if sub_comp is None:
            return;

        if sub_comp.sub_selector is not None\
        and sub_comp.selector is None:
            sub_comp.selector = self.selector + ' > ' + sub_comp.sub_selector;

        sub_comp.parent = self;
