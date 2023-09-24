from abc import ABC, abstractmethod


class MangaDl(ABC):
    @abstractmethod
    def get_chapters(self):
        pass

    @abstractmethod
    def get_chapter_imgs(self):
        pass
    
    @abstractmethod
    def search(self):
        pass
