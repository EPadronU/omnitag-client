#~ cache.py ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Class for manage the configuration-files' cache.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~ Modules ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import atexit
import json
import os
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~ Constants ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
CFG_FILES = {
    'auto-tags': {
        'filename': 'auto-tags.json',
        'default-content': {},
    },
    'black-list': {
        'filename': 'black-list.json',
        'default-content': [],
    },
    'white-list': {
        'filename': 'white-list.json',
        'default-content': [],
    },
    'crawled-resources': {
        'filename': 'crawled-resources.json',
        'default-content': [],
    },
    'settings': {
        'filename': 'settings.json',
        'default-content': {
            'client': '127.0.0.1:5005',
            'server': '127.0.0.1:5000',
            'user-token': '',
            'device-token': '',
            'backup': {
                'interval': 180,
                'intervals': (
                    ('1 minute', 60),
                    ('3 minutes', 180),
                    ('5 minutes', 300),
                    ('10 minutes', 600),
                    ('30 minutes', 1800)
                ),
            },
            'sync': {
                'interval': 300,
                'intervals': (
                    ('5 minutes', 300),
                    ('10 minutes', 600),
                    ('30 minutes', 1800)
                ),
            },
        },
    },
}
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~ Classes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Cache(object):
    def __init__(self, basedir=None):
        self.basedir = basedir or self.__get_default_basedir()
        self.__dict = {}

        self.__load()
        self.__check_state()

        atexit.register(self.dump)

    def __get_default_basedir(self):
        basedir = os.path.join(os.path.realpath(os.path.curdir), '.config')
        if not os.path.exists(basedir): os.mkdir(basedir)
        return basedir

    def __check_state(self):
        assert isinstance(self.basedir, str)
        assert isinstance(self.__dict, dict)

        if not os.path.isdir(self.basedir):
            raise AssertionError('The "{0}" path does not point to a directory'.format(self.basedir))

        for fname, fproperties in CFG_FILES.iteritems():
            if fname not in self.__dict:
                raise AssertionError('The cache does not contain the "{0}" filename'.format(fname))

            elif isinstance(fproperties['default-content'], dict):
                for key in fproperties['default-content'].iterkeys():
                    if key not in self.__dict[fname]:
                        raise AssertionError('The cache does not contain the "{0}" property'.format(key))

    def __load(self):
        for fname, fproperties in CFG_FILES.iteritems():
            fpath = os.path.join(self.basedir, fproperties['filename'])

            if os.path.isfile(fpath):
                with open(fpath) as fpointer:
                    self.__dict[fname] = json.load(fpointer)

            else:
                self.__dict[fname] = CFG_FILES[fname]['default-content']

            if isinstance(self.__dict[fname], list):
                self.__dict[fname] = set(self.__dict[fname])

    def dump(self):
        self.__check_state()

        for fname, fproperties in CFG_FILES.iteritems():
            fpath = os.path.join(self.basedir, fproperties['filename'])

            with open(fpath, 'w') as fpointer:
                if isinstance(self.__dict[fname], set):
                    json.dump(list(self.__dict[fname]), fpointer, indent=4)

                else:
                    json.dump(self.__dict[fname], fpointer, indent=4)

        self.__check_state()

    def get(self, fname):
        self.__check_state()
        return self.__dict.get(fname)

    def set(self, fname, value):
        self.__dict[fname] = value
        self.__check_state()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~ Main ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == '__main__':
    cache = Cache()
    cache.get('settings')['user-token'] = '2|b66140414104ead8bbb4'
    cache.get('settings')['device-token'] = '2|b66140414104ead8bbb4'
    cache.dump()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
