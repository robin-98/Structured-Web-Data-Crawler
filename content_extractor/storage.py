from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.request import urlretrieve
from hashlib import sha256
import os
from datetime import datetime
import json

class StorageWrapper:

    def __init__(self, storage_base_path, storage_def, target_name):
        self.format = 'text';
        self.pages_per_dir = 1;
        self.target_name = target_name;

        self.path = None;
        self.base_path = './';

        if storage_base_path is not None:
            self.base_path = storage_base_path;

        self.target_directory = urljoin(self.base_path + '/', './' + target_name);

        if storage_def is None:
            return;

        if 'format' in storage_def:
            self.format = storage_def['format'];

        if 'pages_per_dir' in storage_def:
            self.pages_per_dir = storage_def['pages_per_dir'];

        self.pages_in_current_directory = dict();
        self.__current_directory = None;

    def save_meta(self):
        # Dump page url and their file names into a json file
        if self.__current_directory is not None:
            for (file_name, data) in [\
                ('url_to_file.json', self.pages_in_current_directory),\
                ('file_to_url.json', {v: k for k, v in self.pages_in_current_directory.items()})]:
                file_path = self.__current_directory + '/' + file_name;
                with open(file_path, 'w') as f:
                    json.dump(data, f, ensure_ascii = False);

    def current_directory(self, page_url):
        if page_url not in self.pages_in_current_directory \
        and (len(self.pages_in_current_directory) >= self.pages_per_dir \
            or len(self.pages_in_current_directory) == 0):
            # New workspace
            self.pages_in_current_directory.clear();
            sub_dir = sha256((datetime.utcnow().isoformat() + '::' + page_url).encode('utf-8')).hexdigest();
            self.__current_directory = urljoin(self.target_directory + '/', sub_dir);
            if not os.path.exists(self.__current_directory):
                os.makedirs(self.__current_directory);
       
        if page_url not in self.pages_in_current_directory: 
            self.pages_in_current_directory[page_url] = None;

        return self.__current_directory;


    def store_resource(self, resource_url, resource_format, page_url):
        file_name = sha256((datetime.utcnow().isoformat() + '::' + page_url + '::' + resource_url).encode('utf-8')).hexdigest();
        o = urlparse(resource_url);
        if resource_format == 'image':
            file_name += '_' + o.path.split('/')[-1][-20:];
        elif resource_format == 'text':
            file_name += '_raw.txt';
       
        file_path = self.current_directory(page_url) + '/' + file_name;
        urlretrieve(resource_url, file_path);
        return file_name;

    def store_page(self, page_content, page_url):
        file_name = sha256((datetime.utcnow().isoformat() + '::' + page_url).encode('utf-8')).hexdigest();
        if self.format == 'text':
            file_name += '.txt';
        elif self.format == 'json':
            file_name += '.json';
        file_path = self.current_directory(page_url) + '/' + file_name;
        self.pages_in_current_directory[page_url] = file_name;

        if type(page_content) == str:
            with open(file_path, 'w') as f:
                f.write(page_content);
        elif type(page_content) == dict:
            with open(file_path, 'w') as f:
                json.dump(page_content, f, ensure_ascii = False);

        self.save_meta();

        return file_path;

