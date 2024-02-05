from requests import Session
from bs4 import BeautifulSoup
from backend.interfaces import MangaDl
from backend.models import Manga, Chapter


class LermangaOrgDl(MangaDl):
    def __init__(self):
        self.session = Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://lermanga.org/',
            'Alt-Used': 'lermanga.org',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
        })

    def search(self, query: str) -> list[Manga] | bool:
        response = self.session.get(f'https://lermanga.org/?s={query.replace(' ', '+')}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            mangas = []
            for div in soup.find_all('div', {'class': 'flw-item'}):
                a = div.find('a', {'data-jname': True})
                mangas.append(
                    Manga(
                        id=a['href'].split('/')[-2],
                        name=a.text,
                        folder_name=a['href'].split('/')[-2],
                        cover=div.find('img')['src']
                    )
                )
            return mangas[:10]
        return False
            
    def get_chapters(self, manga_id: str) -> list[Chapter] | bool:
        response = self.session.get(f'https://lermanga.org/mangas/{manga_id}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            chapters = []
            for a in soup.find('div', {'class': 'manga-chapters'}).find_all('a'):
                chapters.append(
                    Chapter(
                        id=a['href'].split('/')[-2],
                        number=a['href'].split('/')[-2].split('-')[-1],
                        title=a.text
                    )
                )
            return chapters
        return False
    
    def get_chapter_imgs(self, chapter_id: str) -> list[str] | bool:
        response = self.session.get(f'https://lermanga.org/capitulos/{chapter_id}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            link = soup.find('link', {'rel': 'alternate', 'type': 'application/json', 'href': True})
            if link:
                response = self.session.get(link['href'])
                if response.status_code == 200:
                    s = response.json()['content']['rendered']
                    s = s.replace('<p>', '').replace('</p>', '').replace('\n', '').replace('\\', '').replace(' ', '')
                    return s.split('<br/>')
                # well, there's a lot of replaces, but actually I won :)
        return False
    