import json
import re
from functools import cache
from requests import Session
from backend.interfaces import MangaDl
from backend.models import Manga, Chapter
from backend.utilities import clean_str


class MangaDojoDl(MangaDl):
    def __init__(self) -> None:
        self.base_url = 'https://mangadojo.netlify.app'
        self.api_url = 'https://cubari.moe/read/api'
        self.session = Session()
        self.session.headers.update({
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'dnt': '1',
            'priority': 'u=1',
            'referer': 'https://mangadojo.netlify.app/',
            'sec-ch-ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'script',
            'sec-fetch-mode': 'no-cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        })

    @cache
    def get_mangas(self) -> list[Manga] | bool:
        response = self.session.get(f'{self.base_url}/js/dados.js')
        if response.status_code == 200:
            cleaned_text = ''
            for line in response.text.splitlines():
                if not line.strip().startswith('//'):
                    if '// ' in line:
                        line = line.split('//')[0]
                    cleaned_text += line
            print(cleaned_text)
            results = json.loads(
                (re.search(
                    r'var MANGAS = (.*)]', cleaned_text
                ).group(1) + ']')[::-1].replace(',', '', 1)[::-1]
            )
            mangas = []
            for manga in results:
                if 'mangadex' in manga['allLinks']:
                    continue
                mangas.append(
                    Manga(
                        id=manga['allLinks'].split('/')[-2],
                        name=manga['name'],
                        folder_name=clean_str(manga['name']),
                        author=manga['author'],
                        cover=f'{self.base_url}/{manga['img'][1:]}',
                        grade=0.0
                    )
                )
            return mangas
        return False
    def search(self, query: str) -> list[Manga] | bool:
        mangas: list[Manga] = self.get_mangas()
        if not mangas:
            return False
        sorted_mangas = []
        for manga in mangas:
            manga.grade = 0.0
            if query.lower() in manga.name.lower():
                manga.grade += 1
            if manga.name.lower().startswith(query.lower()):
                manga.grade += 1
            if query.lower() in manga.name.lower().split(' '):
                manga.grade += 0.5
            if query.lower() in manga.author.lower():
                manga.grade += 0.5
            if manga.grade:
                sorted_mangas.append(manga)
        sorted_mangas.sort(key=lambda x: x.grade, reverse=True)
        return sorted_mangas[:10]
    
    def get_chapters(self, manga_id: str) -> list[Chapter] | bool:
        response = self.session.get(
            f'{self.api_url}/gist/series/{manga_id}'
        )
        if response.status_code == 200:
            chapters = []
            for chapter_number, chapter in response.json()['chapters'].items():
                chapters.append(
                    Chapter(
                        id='/'.join(list(chapter['groups'].values())[0].split('/')[-3:]),
                        number=float(chapter_number),
                        title=chapter['title'],
                    )
                )
            chapters.sort(key=lambda x: x.number)
            for chapter in chapters:
                if chapter.number.is_integer():
                    chapter.number = int(chapter.number)
            return chapters[::-1]
        return False
    
    def get_chapter_imgs(self, chapter_id: str) -> list[str] | bool:
        response = self.session.get(
            f'{self.api_url}/{chapter_id}'
        )
        if response.status_code == 200:
            return [img['url'] if type(img) == dict else img for img in response.json()['images']]
        return False
    