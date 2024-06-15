import re

import requests
from bs4 import BeautifulSoup
from backend.interfaces import MangaDl
from backend.managers import ThreadManager
from backend.models import Manga, Chapter
from backend.utilities import conditional_cache_lru


class ReadAllComicsDl(MangaDl):
    def __init__(self):
        self.base_url = 'https://readallcomics.com/'
        self.session = requests.Session()
        self.session.headers.update({
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        })

    @conditional_cache_lru(maxsize=1024)
    def get_cover(self, hq_id: str) -> str:
        response = self.session.get(f'{self.base_url}category/{hq_id}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup.find('div', {'class': 'description-archive'}).find('img')['src']
        return ''
    
    def get_number_or_full_name(self, name: str) -> str:
        match = re.search(r'\b(\d+(\.\d+)?)\b', name)
        if match:
            return match.group(1)
        else:
            return name
    
    def search(self, query: str) -> list[Manga] | bool:
        response = self.session.get(
            self.base_url,
            params={
                's': '',
                'story': query,
                'type': 'comic'
            }
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            hqs: list[Manga] = []
            covers_thr = ThreadManager()
            for a in soup.find('ul', {'class': 'list-story categories'}).find_all('a')[:10]:
                hqs.append(
                    Manga(
                        id=a['href'].split('/')[-2],
                        name=a['title'],
                        folder_name=a['href'].split('/')[-2],
                        cover=''
                    )
                )
                covers_thr.add_thread_by_args(
                    self.get_cover, 
                    (a['href'].split('/')[-2],)
                )
            covers_thr.start()
            for hq, cover in zip(hqs, covers_thr.join()):
                hq.cover = cover
            return hqs
        return False
    
    def get_chapters(self, hq_id: str) -> list[Chapter] | bool:
        response = self.session.get(f'{self.base_url}category/{hq_id}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            chapters: list[Chapter] = []
            for a in soup.find('ul', {'class': 'list-story'}).find_all('a'):
                chapters.append(
                    Chapter(
                        id=a['href'].split('/')[-2],
                        number=self.get_number_or_full_name(a.text),
                        title=a.text
                    )
                )
            return chapters
        return False

    def get_chapter_imgs(self, chapter_id: str) -> list[str] | bool:
        response = self.session.get(f'{self.base_url}{chapter_id}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            imgs: list[str] = []
            for img in soup.find_all('img')[1:]:
                imgs.append(img['src'])
            return imgs
        return False
