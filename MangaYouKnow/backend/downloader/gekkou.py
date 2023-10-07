import requests
from bs4 import BeautifulSoup
from backend.interfaces import MangaDl


class GekkouDl(MangaDl):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://gekkou.com.br',
            'Alt-Used': 'gekkou.com.br',
            'Connection': 'keep-alive',
            'Referer': 'https://gekkou.com.br/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        })

    def search(self, entry:str) -> list | bool:
        response = self.session.post(
            f'https://gekkou.com.br/',
            params = {
                's': entry,
                'action': 'wp-manga-search-manga',
                'post_type': 'wp-manga',
                'author': '',
                'artist': '',
                'release': '',
                'adult': ''
            }
        )
        if not response:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        manga_list = []
        for manga in soup.find_all('div', {'class': 'tab-thumb c-image-hover'}):
            link = manga.find('a')
            manga_list.append({
                'id': link['href'].split('/')[-2],
                'name': link['title'],
                'folder_name': link['href'].split('/')[-2],
                'cover': manga.find('img')['data-src']
            })
        return manga_list[:10]

    def get_chapters(self, manga_name) -> list | bool:
        response = self.session.post(f'https://gekkou.com.br/manga/{manga_name.replace(" ", "-")}/ajax/chapters/')
        if not response:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        list_chapters = []
        for a in soup.find_all('a', {'href': True}):
            if a['href'] !='#' and a['href'].replace('https://gekkou.com.br/manga/', '') not in [i['id'] for i in list_chapters]: 
                list_chapters.append({
                    'id': a['href'].replace('https://gekkou.com.br/manga/', ''),
                    'number': a['href'].split('/')[-2],
                    'title': a.text
                })
        return list_chapters
        # works w

    def get_chapters_url(self, manga_name) -> list | bool:
        response = self.session.post(f'https://gekkou.com.br/manga/{manga_name.replace(" ", "-")}/ajax/chapters/')
        if not response:
            return False
        soup = BeautifulSoup(response.content, 'html.parser')
        list_chapters = []
        for a in soup.find_all('a'):
            if a['href'] != '#' and a['href'] not in list_chapters: 
                list_chapters.append(a['href'])
        return list_chapters
    
    def get_chapter_imgs(self, chapter_id) -> list | bool:
        response = self.session.get(
            f'https://gekkou.com.br/manga/{chapter_id}',
            params={'style': 'list'}
        )
        if not response:
            return False
        list_imgs = []
        soup = BeautifulSoup(response.text, 'html.parser')
        for div in soup.find_all('div', {'class': 'page-break '}):
            list_imgs.append(div.find('img')['data-src'].replace('\t\t\t\n\t\t\t', ''))
        return list_imgs

