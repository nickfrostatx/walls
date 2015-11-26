# -*- coding: utf-8 -*-
"""
Random Flickr wallpapers.

:copyright: (c) 2015 by Nicholas Frost.
:license: MIT, see LICENSE for more details.
"""

import flickrapi
import os.path
import sys
try:
    # Python 3.x
    from configparser import ConfigParser
except ImportError:
    # Python 2.x
    from ConfigParser import SafeConfigParser as ConfigParser


__author__ = 'Nick Frost'
__copyright__ = 'Copyright 2015, Nicholas Frost'
__license__ = 'MIT'
__version__ = '0.1.0'
__email__ = 'nickfrostatx@gmail.com'


class Walls(object):

    """The main object."""

    def __init__(self, config):
        self.config = config
        self.flickr = flickrapi.FlickrAPI(config.get('walls', 'api_key'),
                                          config.get('walls', 'api_secret'))

    def download_photo(self):
        photo = first_photo()

    def first_photo():
        results = flickr.walk(tags=config.get('walls', 'tags'), format='json')
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
    config = ConfigParser()

    if len(args) == 1:
        path = os.path.expanduser('~/.wallsrc')
    elif len(args) == 2:
        path = args[1]
    else:
        stderr_and_exit('Usage: walls [config_file]\n')

    if len(config.read(path)) == 0:
        stderr_and_exit("Couldn't load config {0}\n".format(path))
    if not config.has_section('walls'):
        stderr_and_exit('Config missing [walls] section\n')

    # Print out all of the missing keys
    keys = ['api_key', 'api_secret', 'tags', 'height', 'width']
    for key in set(keys):
        if config.has_option('walls', key):
            keys.remove(key)
    if keys:
        stderr_and_exit("Missing config keys: '{0}'\n"
                        .format("', '".join(keys)))

    # Parse integer values
    int_keys = ['height', 'width']
    for key in set(int_keys):
        try:
            config.getint('walls', key)
            int_keys.remove(key)
        except ValueError:
            pass
    if int_keys:
        stderr_and_exit("The following must be integers: '{0}'\n"
                        .format("', '".join(int_keys)))

    return config


def main():
    config = load_config(sys.argv)
    walls = Walls(config)
    walls.download_photo()



if __name__ == '__main__':
    main()
