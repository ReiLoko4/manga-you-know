from abc import ABC, abstractmethod


class MangaDl(ABC):
    @abstractmethod
    def get_chapters(self, *args):
        pass

    @abstractmethod
    def get_chapter_imgs(self, *args):
        pass
    
    @abstractmethod
    def search(self, *args):
        pass
