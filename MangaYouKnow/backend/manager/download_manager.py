from backend.downloader import *
from backend.interfaces import MangaDl


class Downloader:
    def __init__(self) -> None:
        self.downloaders = {
            "aoashi": AoAshiDl(),
            "gkk": GekkouDl(),
            "md": MangaDexDl(),
            "mf": MangaFireDl(),
            "ml": MangaLivreDl(),
            "op": OpScansDl(),
            "opex": OpexDl(),
            "tsct": TaoSectScanDl(),
            "tcb": TCBScansDl()
        }

    def match_source(self, source) -> MangaDl | object:
        return self.downloaders[source]

    def search(self, source: str, query: str):
        source = self.match_source(source)
        if source:
            return source.search(query)
        return False

    def get_chapters(self, source: str, source_id: str) -> list[dict] | list | bool:
        source = self.match_source(source)
        if source:
            return source.get_chapters(source_id)
        return False

    def get_chapter_image_urls(self, source: str, chapter_id: str) -> list | list[dict] | bool:
        source = self.match_source(source)
        if source:
            return source.get_chapter_imgs(chapter_id)
        return False
