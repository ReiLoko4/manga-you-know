import requests
from bs4 import BeautifulSoup
from backend.downloader.manga_dl import MangaDl



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

    def get_chapters(self, manga_id) -> list[list[dict]] | bool:
        '''
        manga_id: name of the manga
        lang: languague
        '''
        response = self.session.get(
            f'https://mangafire.to/manga/{manga_id}'
        )
        if not response:
            return False
        return response.text

    def get_chapters_by_language(self, manga_id, lang:str='PT-BR') -> list[dict] | bool:
        '''
        manga_id: name of the manga
        lang: languague

        returns a list of dictionares

        keys:
            number: str\n
            title: str
        '''
        response = self.session.get(
            f'https://mangafire.to/manga/{manga_id}'
        )
        if not response:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        chapters_list = []
        for li  in soup.find('ul', {'class': 'chapter-list lang-chapter', 'data-name': lang.upper()}).find_all('li'):
            chapters_list.append({
                'number': li['data-number'],
                'title': li.find_all('span')[0].text,
            })
        return chapters_list
    
    def get_chapter_imgs(self, manga_id:str, chapter_number:str, lang='pt-br') -> list | bool:
        response = self.session.get(
            f'https://mangafire.to/ajax/read/{manga_id.split(".")[-1]}/list',
            params={'viewby': 'chapter'},
            headers={'Referer': f'https://mangafire.to/read/{manga_id}/{lang}/chapter-{chapter_number}'}
        )
        if not response:
            return False
        
        images = self.session.get(
            'https://mangafire.to/ajax/read/chapter/2040402'
        )

    def search(self, entry:str) -> list[dict] | bool:
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
        soup = BeautifulSoup(response.text, 'html.parser')
        manga_lists = []
        for div in soup.find_all('div', {'class': 'inner'}):
            manga_lists.append({
                'name': div.find('a', {'class':'color-light'})['title'],
                'url': div.find('a', {'class':'color-light'})['href'],
                'languages': [i.replace(' ', '') for i in div.find('div', {'class':'lang'}).text.split('/')],
                'cover': div.find('img')['src']
            })
        return manga_lists
    

    def is_chapters_big(self, chapter):
        return chapter > 1000

    
# print(MangaFireDl().get_chapters_by_language('one-piece.dkw'))
        