#~ manager.py ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# A class for manage the file-system-related operations.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~ Modules ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import time
from cache import Cache
from crawler import Crawler
from daemonThread import DaemonThread
from syncAgent import SyncAgent
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~ Classes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Manager(object):
    def __init__(self, basedir=None):
        self.cache = Cache(basedir)
        self.__check_state()

    def __check_state(self):
        assert isinstance(self.cache, Cache)

    def __backup_thread(self):
        while True:
            self.cache.dump()
            time.sleep(self.get('settings')['backup']['interval'])

    def __sync_thread(self):
        while True:
            try:
                new_resources = Crawler(
                    self.get('black-list'),
                    self.get('white-list'),
                    self.get('crawled-resources'),
                ).crawl()
                SyncAgent(
                    self.get('settings')['server'],
                    self.get('settings')['user-token'],
                    self.get('settings')['device-token'],
                ).sync(list(new_resources))

            except Exception as e:
                print('[ERROR]: While trying to sync: {0}'.format(e.message))

            time.sleep(self.get('settings')['sync']['interval'])

    def add_to_black_list(self, directory):
        return Crawler.add_to_dirlist(self.get('black-list'), directory)

    def add_to_white_list(self, directory):
        return Crawler.add_to_dirlist(self.get('white-list'), directory)

    def get(self, key):
        return self.cache.get(key)

    def start_backup_daemon(self):
        DaemonThread(target=self.__backup_thread).start()

    def start_sync_daemon(self):
        DaemonThread(target=self.__sync_thread).start()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~ Main ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == '__main__':
    manager = Manager()
    manager.start_sync_daemon()
    while True: time.sleep(2)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~