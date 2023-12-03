from abc import ABC, abstractmethod


class MangaDl(ABC):
    @abstractmethod
    def search(self, query: str, *args):
        pass
    
    @abstractmethod
    def get_chapters(self, manga_id: str | int, *args):
        pass

    @abstractmethod
    def get_chapter_imgs(self, chapter_id: str | int, *args):
        pass
