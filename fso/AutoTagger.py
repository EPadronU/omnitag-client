# ~~ AutoTagger.py ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~ Bind tags automatically to the given resources
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# ~~ Modules ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import re
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# ~~ Classes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class AutoTagger(object):
    def __init__(self, patterns_tags):
        assert isinstance(patterns_tags, dict)

        self.regexes_tags = [
            (re.compile(pattern, re.IGNORECASE), tags) for pattern, tags in patterns_tags.iteritems()
        ]

        assert isinstance(self.regexes_tags, list)

    def process(self, resources):
        assert isinstance(resources, set)

        resources_tags = []

        for resource in resources:
            auto_tags = []

            for regex, tags in self.regexes_tags:
                if(regex.match(resource)):
                    auto_tags.extend(tags)

            resources_tags.append((resource, auto_tags))

        assert isinstance(resources_tags, list)

        return resources_tags
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# ~~ Main ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == '__main__':
    from Crawler import Crawler

    crawler = Crawler(white_list=set((
        '..',
    )))

    auto_tagger = AutoTagger({
        r'^.*\.py$': ['python', 'development'],
        r'^.*\.css$': ['css', 'development'],
        r'^.*\.js$': ['javascript', 'development'],
    })

    for resource, tags in auto_tagger.process(crawler.crawl()):
        print(resource, tags)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
