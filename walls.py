# -*- coding: utf-8 -*-
"""
Random Flickr wallpapers.

:copyright: (c) 2015 by Nicholas Frost.
:license: MIT, see LICENSE for more details.
"""

import flickrapi
import os.path
import requests
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
__version__ = '0.1.2'
__email__ = 'nickfrostatx@gmail.com'


def stderr_and_exit(msg):
    """Write out an error message and exit with code 1."""
    sys.stderr.write(msg)
    sys.exit(1)


def load_config(path):
    """Load the config value from various arguments."""
    config = ConfigParser()

    if len(config.read(path)) == 0:
        stderr_and_exit("Couldn't load config {0}\n".format(path))
    if not config.has_section('walls'):
        stderr_and_exit('Config missing [walls] section.\n')

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
    path = os.path.expanduser(config.get('walls', 'image_dir'))
    if not os.path.isdir(path):
        stderr_and_exit('The directory {0} does not exist.\n'
                        .format(config.get('walls', 'image_dir')))

    return config


def clear_dir(path):
    """Empty out the image directory."""
    for f in os.listdir(path):
        f_path = os.path.join(path, f)
        if os.path.isfile(f_path) or os.path.islink(f_path):
            os.unlink(f_path)


def smallest_url(flickr, pid, min_width, min_height):
    """Return the url of the smallest photo above the dimensions.

    If no such photo exists, return None.
    """
    sizes = flickr.photos_getSizes(photo_id=pid, format='parsed-json')
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


def download(url, dest):
    """Download the image to disk."""
    path = os.path.join(dest, url.split('/')[-1])
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return path


def run(config, clear_opt=False):
    """Find an image and download it."""
    flickr = flickrapi.FlickrAPI(config.get('walls', 'api_key'),
                                 config.get('walls', 'api_secret'))
    width = config.getint('walls', 'width')
    height = config.getint('walls', 'height')

    # Clear out the destination dir
    if clear_opt:
        clear_dir(os.path.expanduser(config.get('walls', 'image_dir')))

    # Find an image
    tags = config.get('walls', 'tags')
    for photo in flickr.walk(tags=tags, format='etree'):
        try:
            photo_url = smallest_url(flickr, photo.get('id'), width, height)
            if photo_url:
                break
        except (KeyError, ValueError, TypeError):
            stderr_and_exit('Unexpected data from Flickr.\n')
    else:
        stderr_and_exit('No matching photos found.\n')

    # Download the image
    dest = os.path.expanduser(config.get('walls', 'image_dir'))
    try:
        download(photo_url, dest)
    except IOError:
        stderr_and_exit('Error downloading image.\n')


def main(args=sys.argv):
    """Parse the arguments, and pass the config object on to run."""
    # Don't make changes to sys.argv
    args = list(args)

    # Remove arg[0]
    args.pop(0)

    # Pop off the options
    clear_opt = False
    if '-c' in args:
        args.remove('-c')
        clear_opt = True
    elif '--clear' in args:
        args.remove('--clear')
        clear_opt = True

    if len(args) == 0:
        cfg_path = os.path.expanduser('~/.wallsrc')
    elif len(args) == 1:
        cfg_path = args[0]
    else:
        stderr_and_exit('Usage: walls [-c] [config_file]\n')

    config = load_config(cfg_path)

    run(config, clear_opt)


if __name__ == '__main__':
    main()
