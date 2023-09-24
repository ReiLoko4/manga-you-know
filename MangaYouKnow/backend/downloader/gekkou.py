import requests
from bs4 import BeautifulSoup
from MangaYouKnow.backend.interfaces import MangaDl


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
            'https://gekkou.com.br/wp-admin/admin-ajax.php',
            data = {
                'action': 'wp-manga-search-manga',
                'title': entry
            }
        )
        if not response:
            return False
        if not response.json()['success']:
            return False
        manga_list = []
        for manga in response.json()['data']:
            manga_list.append({
                'id': manga['url'].split('/')[-2],
                'name': manga['title'],
                'folder_name': manga['url'].split('/')[-2],
                'cover': None
            })
        return manga_list

    def get_chapters(self, manga_name) -> list | bool:
        response = self.session.post(f'https://gekkou.com.br/manga/{manga_name.replace(" ", "-")}/ajax/chapters/')
        if not response:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        list_chapters = []
        for a in soup.find_all('a'):
            if a['href'] !='#' and a['href'].split('/')[-2] not in list_chapters: 
                list_chapters.append({
                    'id': a['href'].split('/')[-2],
                    'number': a['href'].split('/')[-2],

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
    
    def get_chapter_imgs(self, manga_name, chapter_num) -> list | bool:
        response = self.session.get(
            f'https://gekkou.com.br/manga/{manga_name.replace(" ", "-")}/{chapter_num}/',
            params={'style': 'list'}
        )
        if not response:
            return False
        list_imgs = []
        soup = BeautifulSoup(response.text, 'html.parser')
        for div in soup.find_all('div', {'class': 'page-break'}):
            list_imgs.append(div.find('img')['data-src'].replace('\t\t\t\n\t\t\t', ''))
        return list_imgs

