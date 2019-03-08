import urllib
import hashlib
import os

class StorageWrapper:

    def __init__(self, storage_base_path, storage_def):
        self.format = 'text';
        self.pages_per_dir = 1;
        self.use_naive_storage = True;

        self.path = None;
        self.base_path = './';

        if storage_base_path is not None:
            self.base_path = storage_base_path;

        if storage_def is None:
            return;

        if 'format' in storage_def:
            self.format = storage_def['format'];
            self.use_naive_storage = False;

        if 'pages_per_dir' in storage_def:
            self.pages_per_dir = storage_def['pages_per_dir'];

    @staticmethod
    def hash_path(base_path, sub_path, sub_directory_name = ''):
        hash_sub_path = hashlib.sha256(sub_path.encode('utf-8')).hexdigest();
        if sub_directory_name == '':
            return urllib.parse.urljoin(base_path + '/', './' + hash_sub_path);
        else:
            return urllib.parse.urljoin( urllib.parse.urljoin(base_path + '/', './' + sub_directory_name) + '/', './' + hash_sub_path);



    # Should be deprecated
    def store_component_naively(self, page_url, target_name, component_instance, component_url = None, component_text = None):
        if self.path is None:
            self.path = StorageWrapper.hash_path(urllib.parse.urljoin(self.base_path + '/', './' + target_name), page_url);
            if not os.path.exists(self.path):
                os.makedirs(self.path);
            # store meta data
            with open(self.path + '/meta.txt', 'w') as f:
                f.write('page_url: ' + page_url);

        file_base_name = component_instance.role + '_' + str(component_instance.index);
        file_name = file_base_name;
        if component_url is not None:
            o = urllib.parse.urlparse(component_url);
            if component_instance.format == 'image':
                file_name += '_' + o.path.split('/')[-1];
            elif component_instance.format == 'text':
                file_name += '_raw.txt';
            
            data_file_name = self.path + '/' + file_name;
            print('data file:', data_file_name);
            urllib.request.urlretrieve(component_url, data_file_name);
        
        if component_text is not None:
            surfix = '.txt';
            if component_instance.format == 'json':
                surfix = '.json';
            data_file_name = self.path + '/' + file_base_name + surfix;
            print('data file:', data_file_name);
            with open(data_file_name, 'w') as f:
                f.write(component_text);

