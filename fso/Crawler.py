# ~~ Crawler.py ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~ Traverse the users' file system, collecting those files that will be tagged.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# ~~ Modules ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# ~~ Classes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Crawler(object):
    @classmethod
    def add_to_dirlist(cls, dirlist, directory):
        assert isinstance(dirlist, set)
        assert isinstance(directory, str) or isinstance(directory, unicode)

        if directory and os.path.isdir(directory):
            dirlist.add(directory)
            return True

        return False

    def __init__(self, black_list=None, white_list=None, crawled_files=None):
        self.black_list = black_list or set()
        self.white_list = white_list or set()
        self.crawled_files = crawled_files or set()

        self.__check_state()

    def __check_state(self):
        assert isinstance(self.black_list, set)
        assert isinstance(self.white_list, set)
        assert isinstance(self.crawled_files, set)

    def __crawl_directory(self, dirname, path):
        assert isinstance(dirname, str) or isinstance(dirname, unicode)
        assert isinstance(path, str) or isinstance(path, unicode)

        return dirname[0] != u'.' and os.path.join(path, dirname) not in self.black_list

    def crawl(self):
        self.__check_state()

        crawled_files = set()
        for directory in self.white_list:
            for path, dirnames, filenames in os.walk(directory):
                crawled_files.update(os.path.join(path, filename) for filename in filenames)
                dirnames[:] = (dirname for dirname in dirnames if self.__crawl_directory(dirname, path))

        new_files = crawled_files.difference(self.crawled_files)

        self.__check_state()

        return new_files
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# ~~ Main ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == '__main__':
    crawler = Crawler(crawled_files=set([
        '/home/nodxine/InProgress/project-euler/fish/002.fish',
        '/home/nodxine/InProgress/project-euler/fish/001.fish'
    ]))

    Crawler.add_to_dirlist(crawler.white_list, '/home/nodxine/InProgress/project-euler')
    Crawler.add_to_dirlist(crawler.black_list, '/home/nodxine/InProgress/project-euler/c')

    for crawled_file in sorted(crawler.crawl()): print crawled_file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
