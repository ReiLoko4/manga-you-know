from typing import Type
from MangaYouKnow.backend.interfaces import IDownloader


class DownloadManager:
    def __init__(self, downloader: IDownloader):
        self.downloader = downloader

    def search_mangas(self, entry: str):
        return self.downloader.search_mangas(entry)

    def get_manga_chapter_images(self, id_release: str):
        return self.downloader.get_manga_chapter_images(id_release)

    def get_manga_chapters(self, manga_id: str, write_data: bool = False):
        return self.downloader.get_manga_chapters(manga_id, write_data)
