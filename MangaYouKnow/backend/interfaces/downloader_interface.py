from abc import ABC, abstractmethod


class IDownloader(ABC):

    @abstractmethod
    def search_mangas(self, entry: str):
        pass

    @abstractmethod
    def get_manga_chapter_images(self, id_release: str):
        pass

    @abstractmethod
    def get_manga_chapters(self, manga_id: str, write_data: bool = False):
        pass
