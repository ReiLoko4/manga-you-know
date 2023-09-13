import requests
from bs4 import BeautifulSoup
from backend.downloader.manga_dl import MangaDl


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

    def search(self, query: str) -> list[dict] | bool:
        mangas = self.get_mangas()
        mangas_by_query = []
        for manga in mangas:
            if query in manga['name']:
                mangas_by_query.append(manga)
        return mangas_by_query if len(mangas_by_query) > 0 else False

    def get_mangas(self) -> list[dict] | bool:
        response = self.session.get('https://tcbscans.com/projects')
        if not response:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        list_mangas = []
        for a in soup.find_all('a'):
            if a.get('href') == None: 
                continue
            if '/mangas' in a.get('href') and a.get('href') not in [i['url'] for i in list_mangas]:
                if len(str(a).split('>')[-2].replace('</a', '')) != 0:
                    list_mangas.append({
                        'name': str(a).split('>')[-2].replace('</a', ''),
                        'url': str(a['href']).replace('/mangas/', '')
                    })
        return list_mangas
    
    def get_chapters(self, manga_url) -> list[dict] | bool:
        response = self.session.get(f'https://tcbscans.com/mangas/{manga_url}')
        if not response:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        chapters_list = []
        for a in soup.find_all('a'):
            if a.get('href') == None:
                continue       
            if '/chapters/' in a['href']:
                chapters_list.append({
                    'number': (str(a.find_all('div')[0]).replace('<div class="text-lg font-bold">', '')).replace('</div>', '').split(' ')[-1],
                    'title': (str(a.find_all('div')[1]).replace('<div class="text-lg font-bold">', '')).replace('</div>', '').split(' ')[-1] if len(str(a.find_all('div')[1])) != 33 else None,
                    'url': str(a['href']).replace('/chapters/', '')
                })
        return chapters_list
        
    def get_chapter_imgs(self, chapter_url) -> list | bool:
        response = self.session.get(f'https://tcbscans.com/chapters/{chapter_url}')
        if not response:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        imgs_list = []
        for img in soup.find_all('img'):
            if img.get('class') == None:
                continue
            if 'fixed-ratio-content' in img['class']:
                imgs_list.append(img['src'])
        return imgs_list
    
    def download_chapter(self, chapter_url) -> bool:
        imgs_list = self.get_chapter_imgs(chapter_url)
        if not imgs_list:
            return False
        # to complete

