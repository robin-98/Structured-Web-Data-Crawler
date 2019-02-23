import sys;
from page_parser import PageParser;

parser = PageParser('test', 'test');

with open(sys.argv[1], 'r') as f:
    content = f.read();
    parser.feed(content);
    body_tag = None;
    for c in parser.components()[0].contents:
        if not isinstance(c, str):
            if c.tag == 'body':
                body_tag = c;
                break;
    for c in body_tag.contents:
        if not isinstance(c, str):
            print(c.tag, c.attrs, c.text());
