from urllib.request import urlopen
from urllib.request import Request
from urllib.error import HTTPError
from content_extractor.page_parser import PageParser
from content_extractor.storage import StorageWrapper
from content_extractor.content_target import ContentTarget
from domain import *
from general import *
import sys;
import random
import time

class Spider:

    project_name = ''
    base_url = ''
    domain_name = ''
    queue_file = ''
    crawled_file = ''
    queue = set()
    crawled = set()

    def __init__(self, project_name, base_url, domain_name, user_agent = None, white_list = None, target_definition = None, sleep = None):
        Spider.project_name = project_name
        Spider.base_url = base_url
        Spider.domain_name = domain_name
        Spider.queue_file = Spider.project_name + '/queue.txt'
        Spider.crawled_file = Spider.project_name + '/crawled.txt'
        Spider.failed_file = Spider.project_name + '/failed.txt'
        Spider.white_list = white_list;
        Spider.target_definition = target_definition;
        Spider.user_agent = user_agent;

        Spider.sleep = None;
        if sleep is not None:
            Spider.sleep = int(sleep);

        Spider.targets = [];
        if target_definition is not None:
            for target_def in target_definition:
                t = ContentTarget(base_url, target_def, storage_base_path = project_name);
                Spider.targets.append(t);

        self.boot()
        self.crawl_page('First spider', Spider.base_url)

    # Creates directory and files for project on first run and starts the spider
    @staticmethod
    def boot():
        create_project_dir(Spider.project_name)
        create_data_files(Spider.project_name, Spider.base_url)
        Spider.queue = file_to_set(Spider.queue_file)
        Spider.crawled = file_to_set(Spider.crawled_file)
        Spider.failed = file_to_set(Spider.failed_file)

    # Updates user display, fills queue and updates files
    @staticmethod
    def crawl_page(thread_name, page_url):
        if page_url not in Spider.crawled:
            print(thread_name + ' now crawling ' + page_url)
            print('Queue ' + str(len(Spider.queue)) + ' | Crawled  ' + str(len(Spider.crawled)))
            (code, links) = Spider.gather_links(page_url);
            if code == 200:
                Spider.add_links_to_queue(links);
                if page_url in Spider.queue:
                    Spider.queue.remove(page_url)
                    Spider.crawled.add(page_url)
                    Spider.update_files()
            else:
                if page_url in Spider.queue:
                    Spider.queue.remove(page_url);
                    Spider.failed.add(page_url)
                    Spider.update_files();

            if Spider.sleep is not None:
                time.sleep(random.random() * 10 + Spider.sleep);

    # Converts raw response data into readable information and checks for proper html formatting
    @staticmethod
    def gather_links(page_url):
        if type(page_url) != str or len(page_url) == 0:
            return set();
        
        html_string = ''
        response = None;
        try:
            response = None;
            if Spider.user_agent is not None:
                req = Request(page_url,
                    data = None,
                    headers = {
                        'User-Agent': Spider.user_agent
                    });
                response = urlopen(req);
            else:
                response = urlopen(page_url);

            if 'text/html' in response.getheader('Content-Type'):
                html_bytes = response.read()
                html_string = html_bytes.decode("utf-8")
            parser = PageParser(Spider.base_url, page_url, Spider.white_list);
            parser.add_targets(Spider.targets);
            parser.feed(html_string)
        except HTTPError as e:
            # raise HTTPError(req.full_url, code, msg, hdrs, fp)
            print('ERROR when requesting url: [', page_url, '], error code:', e.code, ' error message: [', e.msg, '], http headers:', e.hdrs);
            # raise e;
            return (e.code, set())
        return (200, parser.page_links())
        # return set();

    # Saves queue data to project files
    @staticmethod
    def add_links_to_queue(links):
        for url in links:
            if (url in Spider.queue) or (url in Spider.crawled):
                continue
            if Spider.domain_name != get_domain_name(url):
                continue
            Spider.queue.add(url)

    @staticmethod
    def update_files():
        set_to_file(Spider.queue, Spider.queue_file)
        set_to_file(Spider.crawled, Spider.crawled_file)
        set_to_file(Spider.failed, Spider.failed_file)
