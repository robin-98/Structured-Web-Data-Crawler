import re

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

            if c_def_type == 'nth-child'\
            and c_def_value == '1'\
            and c_inst_nth_child == 0:
                is_matched_in_instance = True;

            if not is_matched_in_instance:
                return False;

        # If can NOT find and violation, which means the instance matches all constraints
        return True;