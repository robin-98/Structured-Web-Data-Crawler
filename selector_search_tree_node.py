
class SelectorSearchTreeNode:

    def __init__(self, component = None, selector_node = None):
        self.component = component;
        self.selector_node = selector_node;
        self.children = {};
