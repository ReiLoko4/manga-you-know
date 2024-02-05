import json
import requests
from bs4 import BeautifulSoup
from backend.interfaces import MangaDl
from backend.models import Manga, Chapter


class MangaNexusDl(MangaDl):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
            'Accept': '*/*',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://manganexus.net/',
            'Alt-Used': 'manganexus.net',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        })

    def search(self, query: str) -> list[Manga] | bool:
        response = self.session.get(
            'https://manganexus.net/api/search',
            params={
                'q': query
            }
        )
        if not response:
            return False
        manga_list = []
        for manga in response.json():
            manga_list.append(
                Manga(
                    id=manga['slug'],
                    name=manga['name'],
                    folder_name=manga['slug'],
                    cover=manga['image'],
                    author=manga['author'],
                )
            )
        return manga_list

    def get_chapters(self, chapter_id) -> list[Chapter] | bool:
        response = self.session.get(
            f'https://manganexus.net/manga/{chapter_id}'
        )
        if not response:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        chapters_list = []
        chapters = json.loads(soup.find('script', {'id': '__NEXT_DATA__'}).text)
        for chapter in chapters['props']['pageProps']['chapters']:
            chapters_list.append(
                Chapter(
                    id=chapter['slug'],
                    number=chapter['number'],
                    title=chapter['name'],
                )
            )
        return chapters_list

    def get_chapter_imgs(self, *args):
        pass