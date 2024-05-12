import json
from requests import Session
from bs4 import BeautifulSoup
from backend.interfaces import MangaDl
from backend.models import Manga, Chapter

class RagnarokDl(MangaDl):
    def __init__(self):
        self.session = Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://ragnarokscanlation.com/',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://ragnarokscanlation.com',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        })
    
    def search(self, query: str) -> list[Manga] | bool:
        response = self.session.get(
            'https://ragnarokscanlation.com/', 
            params={
                's': query,
                'post_type': 'wp-manga',
                'op': '',
                'author': '',
                'artist': '',
                'release': '',
                'adult': '',
            }
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            mangas = []
            for div in soup.find_all('div', {'class': 'tab-thumb c-image-hover'}):
                a = div.find('a')
                mangas.append(
                    Manga(
                        id=a['href'].split('/')[-2],
                        name=a['title'],
                        folder_name=a['href'].split('/')[-2],
                        cover=div.find('img')['data-src'],
                    )
                )
            return mangas[:10]
        return False

    def get_chapters(self, manga_id: str) -> list[Chapter] | bool:
        response = self.session.post(
            f'https://ragnarokscanlation.com/manga/{manga_id}/ajax/chapters/'
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            chapters = []
            for chapter in soup.find_all('li', {'class': 'wp-manga-chapter    '}):
                id = '/'.join(chapter.find('a')['href'].split('/')[-3:-2])
                chapters.append(
                    Chapter(
                        id=chapter,
                        number=id.split('capitulo-')[-1]
                    )
                )
            return chapters
        return False

    def get_chapter_imgs(self, chapter_id: str) -> list[str] | bool:
        response = self.session.get(
            f'https://ragnarokscanlation.com/manga/{chapter_id}',
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            imgs = soup.find('script', {'id': 'chapter_preloaded_images'})
        return False
