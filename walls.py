# -*- coding: utf-8 -*-
"""
Random flickr wallpapers.

:copyright: (c) 2015 by Nicholas Frost.
:license: MIT, see LICENSE for more details.
"""

import configparser
import flickrapi
import os.path
import sys


__author__ = 'Nick Frost'
__copyright__ = 'Copyright 2015, Nicholas Frost'
__license__ = 'MIT'
__version__ = '0.1.0'
__email__ = 'nickfrostatx@gmail.com'


class Walls(object):

    """The main object."""

    def __init__(self, config):
        self.config = config
        self.flickr = flickrapi.FlickrAPI(config['walls'], self.api_secret)

    def download_photo(self):
        photo = first_photo()

    def first_photo():
        results = flickr.walk(tags=config['tags'], format='json')
        for photo in results.get('photos', []):
            if self.is_large_enough(photos):
                return photo

    def is_large_enough(self, id):
        return True



def stderr_and_exit(msg):
    sys.stderr.write(msg)
    sys.exit(1)


def load_config(args):
    """Load the config value from various arguments."""
    config = configparser.ConfigParser()

    if len(args) == 1:
        path = os.path.expanduser('~/.wallsrc')
    elif len(args) == 2:
        path = args[1]
    else:
        stderr_and_exit('Usage: walls [config_file]\n')

    if len(config.read(path)) == 0:
        stderr_and_exit("Couldn't load config {0}\n".format(path))
    if 'walls' not in config:
        stderr_and_exit('Config missing [walls] section\n')

    # Print out all of the missing keys
    keys = ['api_key', 'api_secret', 'tags', 'height', 'width']
    for key in set(keys):
        if key in config['walls']:
            keys.remove(key)
    if keys:
        stderr_and_exit("Missing config keys: '{0}'\n"
                        .format("', '".join(keys)))

    # Parse integer values
    int_keys = ['height', 'width']
    for key in set(int_keys):
        try:
            int(config['walls'][key])
            int_keys.remove(key)
        except ValueError:
            pass
    if int_keys:
        stderr_and_exit("The following must be integers: '{0}'\n"
                        .format("', '".join(int_keys)))

    return config['walls']


def main():
    config = load_config(sys.argv)
    walls = Walls(config)
    walls.download_photo()



if __name__ == '__main__':
    main()
