from urllib.request import urlopen
import sys

if len(sys.argv) == 1:
    print('please input the target url as parameter');
    sys.exit(1);

page_url = sys.argv[1];
response = urlopen(page_url)
if 'text/html' in response.getheader('Content-Type'):
    html_bytes = response.read();
    html_string = html_bytes.decode("utf-8");
    print(html_string);
