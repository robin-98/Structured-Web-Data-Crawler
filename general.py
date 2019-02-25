import os
import json

# Each website is a separate project (folder)
def create_project_dir(directory):
    if not os.path.exists(directory):
        print('Creating directory ' + directory)
        os.makedirs(directory)


# Create queue and crawled files (if not created)
def create_data_files(project_name, base_url):
    queue = os.path.join(project_name , 'queue.txt')
    crawled = os.path.join(project_name,"crawled.txt")
    if not os.path.isfile(queue):
        write_file(queue, base_url)
    if not os.path.isfile(crawled):
        write_file(crawled, '')


# Create a new file
def write_file(path, data):
    with open(path, 'w') as f:
        f.write(data)


# Add data onto an existing file
def append_to_file(path, data):
    with open(path, 'a') as file:
        file.write(data + '\n')


# Delete the contents of a file
def delete_file_contents(path):
    open(path, 'w').close()


# Read a file and convert each line to set items
def file_to_set(file_name):
    results = set()
    with open(file_name, 'rt') as f:
        for line in f:
            results.add(line.replace('\n', ''))
    return results


# Iterate through a set, each item will be a line in a file
def set_to_file(links, file_name):
    with open(file_name,"w") as f:
        for l in sorted(links):
            f.write(l+"\n")

# # Read a file and convert each line to link map
# def file_to_link_map(file_name):
#     result = dict();
#     with open(file_name, 'rt') as f:
#         for line in f:
#             kv = line.split(' ');
#             if len(kv) >= 2:
#                 key = kv[0];
#                 parent_links = kv[1];
#                 if not key in result:
#                     result[key] = [value];
#                 else:
#                     result[key].append(value);
#     return result;

# # Iterate through a link map, store into a file
# def link_map_to_file(link_map, file_name):
#     with open(file_name, 'w') as f:
#         for url in link_map:
#             link = link_map[url];
#             line = link.url + ' '; 
#             for p in link.parent_links:
#                 line += p + ':==:';

#             for t in link.link_texts:
#                 line += ' ' + t;

#             f.write(line + "\n");



# read configurations from json file
def read_configure_file(cfg_file):
    if not os.path.isfile(cfg_file):
        print('can not access file', cfg_file);
        sys.exit(1);

    with open(cfg_file, encoding='utf-8') as f:
        cfg = json.load(f);
        return cfg;