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
width = 1920
height = 1080
    ''')
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
    monkeypatch.setattr('os.path.expanduser', lambda x: str(config))
    cfg = load_config(['walls'])
    assert cfg.get('walls', 'api_key') == 'myapikey'


def test_supplied_config(config):
    """Test a config file passed as a command line argument."""
    cfg = load_config(['walls', config])
    assert cfg.get('walls', 'api_key') == 'myapikey'


def test_invalid_config():
    """"""
