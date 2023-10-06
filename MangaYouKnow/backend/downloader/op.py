import requests
from backend.interfaces import MangaDl


class OpScansDl(MangaDl):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://opscans.com',
            'Origin': 'https://opscans.com',
            'Alt-Used': 'opscans.com',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
        })
    
    def search(self, query: str):
        pass

    def get_chapters(self, manga_id) -> list | bool:
        '''
        manga_id: manga name from site with hyphens
        '''
        response = self.session.get(
            f'https://opscanlations.com/manga/{manga_id}/',
        )
        if not response:
            return False
        print(response.text)

    def get_chapter_imgs(self, chapter_id):
        pass
