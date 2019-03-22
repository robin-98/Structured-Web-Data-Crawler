from urllib.request import urlopen
from urllib.request import Request
import sys

if len(sys.argv) == 1:
    print('please input the target url as parameter');
    sys.exit(1);

page_url = sys.argv[1];

response = None;
if len(sys.argv) > 1:
    req = Request(page_url,
        data = None,
        headers = {
            'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1"
        });
    response = urlopen(req);
else:
    response = urlopen(page_url)

if 'text/html' in response.getheader('Content-Type'):
    html_bytes = response.read();
    html_string = html_bytes.decode("utf-8");
    print(html_string);
