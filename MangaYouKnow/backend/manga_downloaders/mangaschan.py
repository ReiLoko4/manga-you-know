from requests import Session
from bs4 import BeautifulSoup
from backend.interfaces import MangaDl
from backend.models import Manga, Chapter


class MangasChanDl(MangaDl):
    def __init__(self):
        self.session = Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://mangaschan.net',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
        })

    def search(self, query: str) -> list[Manga] | bool:
        response = self.session.get(f'https://mangaschan.net/?s={query.replace(' ', '+')}')
        if response.status_code != 200:
            return False
        soup = BeautifulSoup(response.content, 'html.parser')
        mangas = []
        for div in soup.find_all('div', {'class': 'bs'}):
            a = div.find('a')
            mangas.append(
                Manga(
                    id=a['href'].split('/')[-2],
                    name=a['title'],
                    folder_name=a['href'].split('/')[-2],
                    cover=div.find('img')['src'],
                )
            )
        return mangas[:10]
    
    def get_chapters(self, manga_id: str) -> list[Chapter] | bool:
        response = self.session.get(f'https://mangaschan.net/manga/{manga_id}')
        if response.status_code != 200:
            return False
        soup = BeautifulSoup(response.content, 'html.parser')
        chapters = []
        for li in soup.find('div', {'class': 'eplister'}).find_all('li', {'data-num': True}):
            chapters.append(
                Chapter(
                    id=li.find('a')['href'].split('/')[-2],
                    number=li['data-num'],
                    title=li.find('span', {'class': 'chapternum'}).text
                )
            )
        return chapters
    
    def get_chapter_imgs(self, chapter_id: str) -> list[str] | bool:
        response = self.session.get(f'https://mangaschan.net/{chapter_id}')
        if response.status_code != 200:
            return False
        soup = BeautifulSoup(response.content, 'html.parser')
        pages = []
        for img in soup.find('div', {'id': 'readerarea'}).find_all('img'):
            pages.append(img['src'])
        return pages
