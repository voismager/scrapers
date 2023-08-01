from abc import ABC, abstractmethod


class AbstractExtractor(ABC):
    def extract(self, start_page=1, page_limit=-1):
        if page_limit <= 0:
            last_page = -1
        else:
            last_page = start_page + page_limit - 1

        return self.traverse_and_extract(start_page, last_page)

    @abstractmethod
    def traverse_and_extract(self, start_page, last_page):
        pass
