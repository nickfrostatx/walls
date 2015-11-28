# -*- coding: utf-8 -*-
"""Test walls."""

import flickrapi
import py
import pytest
import requests
import walls
try:
    # Python 3.x
    from configparser import ConfigParser
except ImportError:
    # Python 2.x
    from ConfigParser import SafeConfigParser as ConfigParser


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
def config_obj(config):
    cfg = ConfigParser()
    cfg.read(config)
    return cfg


@pytest.fixture
def flickr():
    return flickrapi.FlickrAPI('myapikey', 'myapisecret')


class FakeResponse(requests.Response):

    """Used to emulate some requests behavior."""

    def __call__(self, *a, **kw):
        """Lets us use an instance to replace get()."""
        return self

    def iter_content(self, *a, **kw):
        for c in 'this is the data':
            yield c.encode()


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
        walls.stderr_and_exit('Some error message')


def test_usage(errmsg):
    """Make sure we print out the usage if the arguments are invalid."""
    with errmsg('Usage: walls [-c] [config_file]\n'):
        walls.main(['walls', 'config_file', 'blah'])


def test_default_config(config, monkeypatch):
    """Override expanduser to point to our temporary config file."""
    def my_expanduser(path):
        if path == '~/.wallsrc':
            return config
        return path
    monkeypatch.setattr('os.path.expanduser', my_expanduser)
    monkeypatch.setattr('walls.run', lambda config: None)
    walls.main(['walls'])


def test_supplied_config(config):
    """Test a config file passed as a command line argument."""
    cfg = walls.load_config(config)
    assert cfg.get('walls', 'api_key') == 'myapikey'


def test_invalid_config(errmsg):
    """Make sure an error is raised if the config file can't be read."""
    with errmsg("Couldn't load config fake.ini\n"):
        walls.load_config('fake.ini')


def test_config_no_walls(tmpdir, errmsg):
    """Check for missing [walls] section."""
    f = tmpdir.join('config.ini')
    f.write('\n')
    with errmsg('Config missing [walls] section.\n'):
        walls.load_config(str(f))


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
        walls.load_config(str(f))


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
        walls.load_config(str(f))


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
        walls.load_config(str(f))

    f = tmpdir.join('config2.ini')
    f.write(cfg.format(f))
    with errmsg('The directory {0} does not exist.\n'.format(f)):
        walls.load_config(str(f))


def test_clear_dir(tmpdir):
    tmpdir.join('a.txt').write('test1')
    tmpdir.join('b.txt').write('test2')
    tmpdir.mkdir('dir').join('nested.txt').write('test3')
    assert len(tmpdir.listdir()) == 3
    walls.clear_dir(str(tmpdir))
    assert len(tmpdir.listdir()) == 1


def test_smallest_url(flickr):
    data = {
        'sizes': {'size': [
            {
                'width': '1280',
                'height': '720',
                'source': 'url1',
            },
            {
                'width': '1920',
                'height': '1080',
                'source': 'url2',
            },
            {
                'width': '2560',
                'height': '1440',
                'source': 'url3',
            },
        ]},
    }
    flickr.photos_getSizes = lambda **kw: data
    assert walls.smallest_url(flickr, 'fake', 1920, 1080) == 'url2'


def test_first_photo_invalid(monkeypatch, config_obj, errmsg):
    data = None
    monkeypatch.setattr('flickrapi.FlickrAPI.photos_getSizes',
                        lambda self, **kw: data, raising=False)
    monkeypatch.setattr('flickrapi.FlickrAPI.walk',
                        lambda self, **kw: [{'id': '1'}])
    for d in [[], {}, {'sizes': 1}, {'sizes': []}, {'sizes': {'size': 1}},
              {'sizes': {'size': [1]}}, {'sizes': {'size': [{}]}}]:
        data = d
        with errmsg('Unexpected data from Flickr.\n'):
            walls.run(config_obj)


def test_run_empty_search(monkeypatch, config_obj, errmsg):
    monkeypatch.setattr('flickrapi.FlickrAPI.walk', lambda self, **kw: [])
    with errmsg('No matching photos found.\n'):
        walls.run(config_obj)


def test_run_bad_request(monkeypatch, config_obj, errmsg):
    def raise_function(*a, **kw):
        raise IOError()
    monkeypatch.setattr('requests.get', raise_function)
    monkeypatch.setattr('flickrapi.FlickrAPI.walk',
                        lambda self, **kw: [{'id': 1}])
    monkeypatch.setattr('walls.smallest_url', lambda *a: 'http://example.com')
    walls.first_photo = lambda: 'url'
    with errmsg('Error downloading image.\n'):
        walls.run(config_obj)


def test_main(monkeypatch, config):
    """Check that the arg parsing all works."""
    c = [False]

    def set_clear(*a):
        """Remember that clear was run."""
        c[0] = True

    def my_expanduser(path):
        if path == '~/.wallsrc':
            return config
        return path

    monkeypatch.setattr('os.path.expanduser', my_expanduser)
    monkeypatch.setattr('walls.clear_dir', set_clear)
    monkeypatch.setattr('walls.run', lambda config: None)

    walls.main(['walls'])
    assert not c[0]

    for args in [['-c'], ['--clear'], ['-c', config], [config, '-c'],
                 ['--clear', config], [config, '--clear']]:
        walls.main(['walls'] + args)
        assert c[0]
        # Reset clear
        c[0] = False


def test_download(monkeypatch, tmpdir):
    resp = FakeResponse()
    resp.status_code = 200
    monkeypatch.setattr('requests.get', resp)
    walls.download('file.txt', str(tmpdir))
    assert tmpdir.join('file.txt').read() == 'this is the data'


def test_download_status(monkeypatch, tmpdir):
    resp = FakeResponse()
    resp.status_code = 418
    monkeypatch.setattr('requests.get', resp)
    with pytest.raises(IOError):
        walls.download('file.txt', str(tmpdir))


def test_download_real_status(monkeypatch, tmpdir):
    with pytest.raises(IOError):
        walls.download('http://0.0.0.0:1234', str(tmpdir))
