import requests
from bs4 import BeautifulSoup
from backend.interfaces import MangaDl
from backend.models import Manga, Chapter


class TCBScansDl(MangaDl):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://tcbscans.com/',
            'Alt-Used': 'tcbscans.com',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
        })

    def search(self, query: str) -> list[Manga] | bool:
        mangas: list[Manga] = self.get_mangas()
        sorted_mangas = []
        for manga in mangas:
            if query.lower() in manga.name.lower():
                sorted_mangas.append(manga)
        return sorted_mangas[:10]

    def get_mangas(self) -> list[Manga] | bool:
        response = self.session.get('https://tcbscans.com/projects')
        if not response:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        mangas = []
        for a in soup.find_all('a', {'href': True}):
            if '/mangas' in a['href'] and a.find('img'):
                    img = a.find('img')
                    mangas.append(
                        Manga(
                            id=str(a['href']).replace('/mangas/', ''),
                            name=img['alt'],
                            folder_name=str(a['href']).split('/')[-1],
                            cover=img['src']
                        )
                    )
        return mangas
    
    def get_chapters(self, manga_id: str) -> list[Chapter] | bool:
        response = self.session.get(f'https://tcbscans.com/mangas/{manga_id}')
        if not response:
            return False
        soup = BeautifulSoup(response.content, 'html.parser')
        chapters_list = []
        for a in soup.find('div', {'class': 'col-span-2'}).find_all('a', {'href': True}):
            divs = a.find_all('div')
            chapters_list.append(
                Chapter(
                    id=str(a['href']).replace('/chapters/', ''),
                    number=divs[0].split(' ')[-1],
                    title=divs[1].text,
                )
            )
        return chapters_list
        
    def get_chapter_imgs(self, chapter_id: str) -> list[str] | bool:
        response = self.session.get(f'https://tcbscans.com/chapters/{chapter_id}')
        if not response:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        chapter_imgs = []
        for img in soup.find_all('img', {'class': True, 'src': True}):
            if 'fixed-ratio-content' in img['class']:
                chapter_imgs.append(img['src'])
        return chapter_imgs
