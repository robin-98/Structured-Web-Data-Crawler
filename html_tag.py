class HtmlTag:
    '''Html Tag instances to wrap sub tags and contents'''
    def __init__(self, tagStr, attrs):
        self.tag = tagStr;
        self.attrs = attrs;

        # array of contents contain tags and paragraphs of text
        self.contents = [];

        self.path = [];

    def addSubTag(self, tagInst):
        self.contents.append(tagInst);


    def addText(self, text):
        self.contents.append(text);


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
        s = '' + self.tag;
        if len(self.attrs) > 0:
            if 'id' in self.attrs:
                s = '#' + self.attrs['id'];
            elif 'class' in self.attrs:
                s += '.' + self.attrs['class'].replace(' ', '.');
        return s;