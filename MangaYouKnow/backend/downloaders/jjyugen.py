from requests import Session
from bs4 import BeautifulSoup
from backend.downloaders import *
from backend.interfaces import MangaDl
from backend.models import Manga, Chapter


class JujutsuYugenDl(MangaDl):
    def __init__(self) -> None:
        self.session = Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://t.co/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
        })

    def search(self) -> list[Manga]:
        pass
        # Isn't needed

    def get_chapters(self, _=None) -> list[Chapter]:
        response = self.session.get(f'https://jujutsuyugen.com/chapters')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            last_chapter = int(soup.find_all('span', {'class': 'page_span__q1mtG'})[0].text.split('\n')[0])
            chapters = []
            for i in range(last_chapter, 0, -1):
                chapters.append(
                    Chapter(
                        id=str(i),
                        number=i,
                        title=str(i)
                    )
                )
            return chapters
        return False

    def get_chapter_imgs(self, chapter_id: str) -> list[str]:
        response = self.session.get(f'https://jujutsuyugen.com/chapters/{chapter_id}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return [link['href'] for link in soup.find_all('link', {'rel': 'preload', 'as': 'image'})]
        return False
