class HtmlTag:
    '''Html Tag instances to wrap sub tags and contents'''
    def __init__(self, tagStr, attrs):
        self.tag = tagStr;
        self.attrs = {};
        for (attribute, value) in attrs:
            self.attrs[attribute] = value;

        # array of contents contain tags and paragraphs of text
        self.contents = [];

        self.nth_child = 0;

    def addSubTag(self, tagInst):
        self.contents.append(tagInst);


    def addText(self, text):
        self.contents.append(text);

    def sub_tags(self):
        return [c for c in self.contents if type(c) == HtmlTag];

    def all_sub_selectors(self):
        result = [];
        self_selector = self.selector();
        for t in self.sub_tags():
            s = self_selector + ' > ' + t.selector();
            result.append({'tag': t, 'selector': s});
            for st in t.all_sub_selectors():
                st['selector'] = self_selector + ' > ' + st['selector'];
                result.append(st);
        return result;


    def text(self):
        content = '';
        for c in self.contents:
            if isinstance(c, HtmlTag):
                content += c.text();
            elif isinstance(c, str):
                content += c;

        return content;

    def is_using_id(self):
        if len(self.attrs) > 0 and 'id' in self.attrs:
            return True;
        else:
            return False;

    # gennerate the jQuery style element selector for the tag instance
    def selector(self):
        result = self.selector_without_nth_child();
        if self.nth_child > 0:
            result += ':nth-child(' + str(self.nth_child) + ')';
        return result;

    def selector_only_nth_child(self):
        result = self.tag;
        if self.nth_child > 0:
            result += ':nth-child(' + str(self.nth_child) + ')';
        return result;

    def selector_without_nth_child(self):
        result = self.tag;
        if 'id' in self.attrs:
            result = '#' + self.attrs['id'];
        else:
            if 'class' in self.attrs:
                class_str = self.attrs['class'].replace(' ', '.').strip();
                if class_str != '':
                    result += '.' + class_str;
            for a in self.attrs:
                if a not in ['id', 'class']:
                    v = self.attrs[a];
                    if v is not None:
                        result += ':' + a + '=' + self.attrs[a];
                    else:
                        result += ':' + a + '=true';
        return result;

