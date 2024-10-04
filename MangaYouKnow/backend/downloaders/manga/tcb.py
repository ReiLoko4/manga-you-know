from functools import cache
from requests import Session
from bs4 import BeautifulSoup
from backend.interfaces import MangaDl
from backend.models import Manga, Chapter


class TCBScansDl(MangaDl):
    def __init__(self):
        self.base_url = 'https://tcbscans.me/'
        self.session = Session()
        self.session.headers.update({
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'dnt': '1',
            'priority': 'u=0, i',
            'referer': 'https://tcbscans.me/',
            'sec-ch-ua': '"Chromium";v="125", "Not.A/Brand";v="24"',
            'sec-ch-ua-arch': '"x86"',
            'sec-ch-ua-bitness': '"64"',
            'sec-ch-ua-full-version': '"125.0.6422.112"',
            'sec-ch-ua-full-version-list': '"Chromium";v="125.0.6422.112", "Not.A/Brand";v="24.0.0.0"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"15.0.0"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        })

        
    @cache
    def get_mangas(self) -> list[Manga] | bool:
        response = self.session.get(f'{self.base_url}projects')
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

    def search(self, query: str) -> list[Manga] | bool:
        mangas: list[Manga] = self.get_mangas()
        sorted_mangas = []
        for manga in mangas:
            if query.lower() in manga.name.lower():
                sorted_mangas.append(manga)
        return sorted_mangas[:10]

    def get_chapters(self, manga_id: str) -> list[Chapter] | bool:
        response = self.session.get(f'{self.base_url}mangas/{manga_id}')
        if not response:
            return False
        soup = BeautifulSoup(response.content, 'html.parser')
        chapters_list = []
        for a in soup.find('div', {'class': 'col-span-2'}).find_all('a', {'href': True}):
            divs = a.find_all('div')
            chapters_list.append(
                Chapter(
                    id=str(a['href']).replace('/chapters/', ''),
                    number=divs[0].text.split(' ')[-1],
                    title=divs[1].text,
                )
            )
        return chapters_list
        
    def get_chapter_imgs(self, chapter_id: str) -> list[str] | bool:
        response = self.session.get(f'{self.base_url}chapters/{chapter_id}')
        if not response:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        chapter_imgs = []
        for img in soup.find_all('img', {'class': True, 'src': True}):
            if 'fixed-ratio-content' in img['class']:
                chapter_imgs.append(img['src'])
        return chapter_imgs
