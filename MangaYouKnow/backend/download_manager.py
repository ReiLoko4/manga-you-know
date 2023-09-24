from backend.downloader import *

class Downloader:
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
            case 'gkk' | 'gkk_id':
                return self.gekkou
            case 'md' | 'md_id':
                return self.mangadex
            case 'mf' | 'mf_id':
                return self.mangafire
            case 'ml' | 'ml_id':
                return self.mangalivre
            case 'op' | 'op_id':
                return self.op
            case 'opex' | 'opex_id':
                return self.opex
            case 'tsct' | 'tsct_id':
                return self.tsct
            case 'tcb' | 'tcb_id':
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
