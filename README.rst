walls
=====

.. image:: https://img.shields.io/travis/nickfrostatx/walls.svg
    :target: https://travis-ci.org/nickfrostatx/walls

.. image:: https://img.shields.io/coveralls/nickfrostatx/walls.svg
    :target: https://coveralls.io/github/nickfrostatx/walls

.. image:: https://img.shields.io/pypi/v/walls.svg
    :target: https://pypi.python.org/pypi/walls

.. image:: https://img.shields.io/pypi/l/walls.svg
    :target: https://raw.githubusercontent.com/nickfrostatx/walls/master/LICENSE

``walls`` downloads random wallpapers from Flickr. It searches recent Flickr
images matching a given list of tags, and downloads the first one with
dimensions large enough to be used as a wallpaper.

Installation
------------

.. code-block:: bash

    $ pip install walls

Config
------

The default config location is ``~/.wallsrc``. Here is an example configuration:

.. code-block:: ini

    [walls]
    api_key = YOUR_API_KEY
    api_secret = YOUR_API_SECRET
    tags = cats,dogs
    image_dir = ~/Pictures
    width = 1920
    height = 1080

Usage
-----

.. code-block:: bash

    $ walls [config_file]

If supplied, ``config_file`` will be used instead of ``~/.wallsrc``.
