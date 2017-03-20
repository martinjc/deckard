#!/usr/bin/env python
#

import os
import json

"""
JSONFileCache provides a local cache of JSON files,
stored in the directory 'cache' under the current
working directory
"""

class JSONFileCache(object):

    def __init__(self):

        cwd_dir = os.getcwd()

        # directory for cache
        self.cache_dir = os.path.join(cwd_dir, 'cache')
        if not os.path.isdir(self.cache_dir):
            os.makedirs(self.cache_dir)

    # check whether a file exists in the cache
    def file_exists(self, file_id):
        return os.path.isfile(os.path.join(self.cache_dir, file_id))

    # retrieve json from the cache
    def get_json(self, file_id):
        assert self.file_exists(file_id)

        with open(os.path.join(self.cache_dir, file_id), "r") as infile:
            return json.load(infile)

    # store some json in the cache
    def put_json(self, json_data, file_id):
        with open(os.path.join(self.cache_dir, file_id), "w") as outfile:
            json.dump(json_data, outfile)

    # store some text
    def put_text(self, text, file_id):
        with open(os.path.join(self.cache_dir, file_id), "w") as outfile:
            outfile.write(text)

    # retrieve text from the cache
    def get_text(self, file_id):
        assert self.file_exists(file_id)

        with open(os.path.join(self.cache_dir, file_id), "r") as infile:
            return infile.read()
