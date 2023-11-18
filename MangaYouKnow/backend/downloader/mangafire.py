import requests
from bs4 import BeautifulSoup
from backend.interfaces import MangaDl
from backend.models import Manga, Chapter


class MangaFireDl(MangaDl):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://mangafire.to/',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Connection': 'keep-alive',
            'Alt-Used': 'mangafire.to',
        })

    def search(self, entry: str) -> list[Manga] | bool:
        '''
        entry: a string with the query to search the manga you want

        ---

        returns a list of dictonaries

        keys:
            name: str\n
            url: str\n
            languages: list\n
            cover: str
        '''
        response = self.session.get(
            'https://mangafire.to/filter',
            params={'keyword': entry}
        )
        if not response:
            return False
        soup = BeautifulSoup(response.content, 'html.parser')
        manga_lists = []
        for div in soup.find_all('div', {'class': 'inner'})[:-1]:
            manga_lists.append(
                Manga(
                    id=div.find('a', {'class': 'poster'})['href'].split('/')[-1].split('.')[-1],
                    name=div.find('img')['alt'],
                    folder_name=div.find('a', {'class': 'poster'})['href'].split('/')[-1],
                    cover=div.find('img')['src']
                )
            )
        return manga_lists[:10]  # to keep igual to the other sources

    def get_chapters(self, manga_id, lang: str = 'PT-BR') -> list[Chapter] | bool:
        '''
        manga_id: name of the manga
        lang: languague
        '''
        response = self.session.get(
            f'https://mangafire.to/ajax/read/{manga_id}/chapter/en'
        )
        if not response:
            return False
        soup = BeautifulSoup(response.content, 'html.parser')
        chapters_list = []
        for li in soup.find('ul').find_all('li'):
            a = li.find('a')
            chapters_list.append(
                Chapter(
                    id=a['data-id'].replace('\\', '').replace('"', ''),
                    number=a['data-number'].replace('\\', '').replace('"', ''),
                    title=a['title'],
                )
            )
        return chapters_list

    def get_chapter_imgs(self, chapter_id: str, lang='pt-br') -> list | bool:
        response = self.session.get(
            f'https://mangafire.to/ajax/read/chapter/{chapter_id}',
            # headers={'Referer': f'https://mangafire.to/read/{manga_id}/{lang}/chapter-{chapter_number}'}
        )
        if not response:
            return False
        return [i[0] for i in response.json()['result']['images']]

    def is_chapters_big(self, chapter):
        return chapter > 1000