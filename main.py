import threading
from queue import Queue
from spider import Spider
from domain import *
from general import *
import sys

# read the onfigure file
if (len(sys.argv) == 1):
  print ('Please input the config file name/path');
  sys.exit(1);

cfg_file = sys.argv[1];
cfg = read_configure_file(cfg_file);

if "Structured-Web-Data-Crawler" not in cfg:
    print('Structured Web Data Crawler is not configured');
    sys.exit(1);

cfg = cfg["Structured-Web-Data-Crawler"];
# end of read configure file

target_site_index = -1;
if len(sys.argv) > 2:
    target_site_index = int(sys.argv[2]);


# Read projects
if "target_sites" not in cfg:
    print('can not find target sites in the configure');
    sys.exit(1);

data_dir = cfg["data_dir"];
idx = -1;
for site in cfg["target_sites"]:
  idx += 1;
  if target_site_index >=0 and idx != target_site_index:
    continue;

  PROJECT_NAME = data_dir + '/' + site['project_name'] +'/' + site['version'];
  HOMEPAGE = site['base_url'];
  DOMAIN_NAME = get_domain_name(HOMEPAGE);
  QUEUE_FILE = PROJECT_NAME + '/queue.txt'
  CRAWLED_FILE = PROJECT_NAME + '/crawled.txt'
  NUMBER_OF_THREADS = site['threads'];
  WHITE_LIST = site['white_list'];
  TARGET_DEFINITION = site['target_components'];
  queue = Queue()
  Spider(PROJECT_NAME, HOMEPAGE, DOMAIN_NAME, WHITE_LIST, TARGET_DEFINITION)

  # Create worker threads (will die when main exits)
  def create_workers():
    for _ in range(NUMBER_OF_THREADS):
      t = threading.Thread(target=work)
      t.daemon = True
      t.start()

  # Do the next job in the queue
  def work():
    while True:
      url = queue.get()
      Spider.crawl_page(threading.current_thread().name, url)
      queue.task_done()

  # Each queued link is a new job
  def create_jobs():
    for link in file_to_set(QUEUE_FILE):
      queue.put(link)
    queue.join()
    crawl()

  # Check if there are items in the queue, if so crawl them
  def crawl():
    queued_links = file_to_set(QUEUE_FILE)
    if len(queued_links) > 0:
      print(str(len(queued_links)) + ' links in the queue')
      create_jobs()

  create_workers()
  crawl()  


