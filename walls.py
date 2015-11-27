# -*- coding: utf-8 -*-
"""
Random Flickr wallpapers.

:copyright: (c) 2015 by Nicholas Frost.
:license: MIT, see LICENSE for more details.
"""

import flickrapi
import os.path
import py
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


def stderr_and_exit(msg):
    """Write out an error message and exit with code 1."""
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
    keys = ['api_key', 'api_secret', 'tags', 'image_dir', 'width', 'height']
    for key in set(keys):
        if config.has_option('walls', key):
            keys.remove(key)
    if keys:
        stderr_and_exit("Missing config keys: '{0}'\n"
                        .format("', '".join(keys)))

    # Parse integer values
    int_keys = ['width', 'height']
    for key in set(int_keys):
        try:
            config.getint('walls', key)
            int_keys.remove(key)
        except ValueError:
            pass
    if int_keys:
        stderr_and_exit("The following must be integers: '{0}'\n"
                        .format("', '".join(int_keys)))

    # Check destination directory
    path = py.path.local(config.get('walls', 'image_dir'), expanduser=True)
    if not path.isdir():
        stderr_and_exit('The directory {0} does not exist.\n'
                        .format(config.get('walls', 'image_dir')))

    return config


class Walls(object):

    """The main object."""

    def __init__(self, config):
        """Initial setup."""
        self.config = config
        self.flickr = flickrapi.FlickrAPI(config.get('walls', 'api_key'),
                                          config.get('walls', 'api_secret'))

    def run(self):
        """Find a photo, download it to disk."""
        photo_url = self.first_photo()
        if not photo_url:
            stderr_and_exit('No matching photos found.\n')
        print(photo_url)

    def first_photo(self):
        """Find the id of the first criteria-matching photo."""
        tags = self.config.get('walls', 'tags')
        for photo in self.flickr.walk(tags=tags, format='etree'):
            try:
                url = self.smallest_url(photo.get('id'))
            except (KeyError, ValueError):
                stderr_and_exit('Unexpected data from Flickr.\n')
            if url:
                return url

    def smallest_url(self, pid):
        """Return the url of the smallest photo above the dimensions.

        If no such photo exists, return None.
        """
        sizes = self.flickr.photos_getSizes(photo_id=pid, format='parsed-json')
        min_width = self.config.getint('walls', 'width')
        min_height = self.config.getint('walls', 'height')
        smallest_url = None
        smallest_area = None
        for size in sizes['sizes']['size']:
            width = int(size['width'])
            height = int(size['height'])
            # Enforce a minimum height and width
            if width >= min_width and height >= min_height:
                if not smallest_url or height * width < smallest_area:
                    smallest_area = height * width
                    smallest_url = size['source']
        return smallest_url


def main():
    """Run the downloader from the command line."""
    config = load_config(sys.argv)
    walls = Walls(config)
    walls.run()


if __name__ == '__main__':
    main()
