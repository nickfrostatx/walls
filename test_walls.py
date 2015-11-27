# -*- coding: utf-8 -*-
"""Test walls."""

from contextlib import contextmanager
from walls import Walls, load_config, stderr_and_exit, main
import os.path
import pytest


@pytest.fixture
def config(tmpdir):
    f = tmpdir.join('config.ini')
    f.write('''
[walls]
api_key = myapikey
api_secret = myapisecret
tags = sanfrancisco
image_dir = {0}
width = 1920
height = 1080
    '''.format(tmpdir))
    return str(f)


@pytest.fixture
def walls(config):
    """Create a Walls object with a default config."""
    cfg = load_config(config)
    return Walls(cfg)


class SystemExitContext(object):

    """Run pytest.raises, and check the error message."""

    def __init__(self, msg, capsys):
        self.raises = pytest.raises(SystemExit)
        self.capsys = capsys
        self.msg = msg

    def __enter__(self):
        return self.raises.__enter__()

    def __exit__(self, *args):
        assert self.capsys.readouterr()[1] == self.msg
        return self.raises.__exit__(*args)


@pytest.fixture
def errmsg(capsys):
    """Make sure we exit with the given error message."""
    def fixture(msg):
        return SystemExitContext(msg, capsys)
    return fixture


def test_stderr_and_exit(errmsg):
    """Make sure that stderr_and_exit (and therefore errmsg) works."""
    with errmsg('Some error message'):
        stderr_and_exit('Some error message')


def test_usage(errmsg):
    """Make sure we print out the usage if the arguments are invalid."""
    with errmsg('Usage: walls [config_file]\n'):
        load_config(['walls', 'config_file', 'blah'])


def test_default_config(config, monkeypatch):
    """Override expanduser to point to our temporary config file."""
    def my_expanduser(path):
        if path == '~/.wallsrc':
            return str(config)
        return path
    monkeypatch.setattr('os.path.expanduser', my_expanduser)
    cfg = load_config(['walls'])
    assert cfg.get('walls', 'api_key') == 'myapikey'


def test_supplied_config(config):
    """Test a config file passed as a command line argument."""
    cfg = load_config(['walls', config])
    assert cfg.get('walls', 'api_key') == 'myapikey'


def test_invalid_config(errmsg):
    """Make sure an error is raised if the config file can't be read."""
    with errmsg("Couldn't load config fake.ini\n"):
        load_config(['walls', 'fake.ini'])


def test_config_missing(tmpdir, errmsg):
    """Check behavior on missing config values."""
    f = tmpdir.join('config.ini')
    f.write('''
[walls]
api_secret = myapisecret
image_dir = {0}
width = 1920
height = 1080
    '''.format(tmpdir))
    with errmsg("Missing config keys: 'api_key', 'tags'\n"):
        load_config(['walls', str(f)])


def test_config_types(tmpdir, errmsg):
    """Check behavior on missing config values."""
    f = tmpdir.join('config.ini')
    f.write('''
[walls]
api_key = myapikey
api_secret = myapisecret
tags = sanfrancisco
image_dir = {0}
width = abc
height = def
    '''.format(tmpdir))
    with errmsg("The following must be integers: 'width', 'height'\n"):
        load_config(['walls', str(f)])


def test_config_dest(tmpdir, errmsg):
    """Nonexistent destination directory."""
    cfg = '''
[walls]
api_key = myapikey
api_secret = myapisecret
tags = sanfrancisco
image_dir = {0}
width = 1920
height = 1080
    '''

    f = tmpdir.join('config1.ini')
    f.write(cfg.format('/does/not/exist'))
    with errmsg('The directory /does/not/exist does not exist.\n'):
        load_config(['walls', str(f)])

    f = tmpdir.join('config2.ini')
    f.write(cfg.format(f))
    with errmsg('The directory {0} does not exist.\n'.format(f)):
        load_config(['walls', str(f)])
