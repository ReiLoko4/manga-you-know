from downloader import *

class Downloader():
    def __init__(self) -> None:
        self.aoashi = AoAshiDl()
        self.gekkou = GekkouDl()
        self.mangadex = MangaDexDl()
        self.mangafire = MangaFireDl()
        self.mangalivre = MangaLivreDl()
        self.op = OpScansDl()
        self.opex = OpexDl()
        self.tsct = TaoSectScanDl()
        self.tcb = TCBScansDl()
 
    def match_source(self, source) -> object:
        match source:
            case 'aoashi':
                return self.aoashi
            case 'gekkou':
                return self.gekkou
            case 'mangadex':
                return self.mangadex
            case 'mangafire':
                return self.mangafire
            case 'mangalivre':
                return self.mangalivre
            case 'op':
                return self.op
            case 'opex':
                return self.opex
            case 'taosect':
                return self.tsct
            case 'tcb':
                return self.tcb
            case _:
                return None
            
    def search(self, source:str, query:str):
        source = self.match_source(source)
        if source:
            return source.search(query)
        return False
            
    def get_chapters(self, source:str, source_id:str) -> list[dict] | list | bool:
        source = self.match_source(source)
        if source:
            return source.get_chapters(source_id)
        return False
    
    def get_chapter_image_urls(self, source:str, chapter_id:str) -> list | list[dict] | bool:
        source = self.match_source(source)
        if source:
            return source.get_chapter_imgs(chapter_id)
        return False
