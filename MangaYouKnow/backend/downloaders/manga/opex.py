import json
import requests
from pathlib import Path
from threading import Thread
from bs4 import BeautifulSoup
from backend.interfaces import MangaDl
from backend.models import Chapter


class OpexDl(MangaDl):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://onepieceex.net/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
        })

    def search():
        # Isn't needed
        pass

    def get_chapters(self, _=None) -> list:
        response =  self.session.get('https://onepieceex.net/mangas/')
        if not response:
            return False
        chapters_list = []
        soup = BeautifulSoup(response.text, 'html.parser')
        for li in soup.find_all('li', {'class': 'volume-capitulo'}):
            a_list = li.find_all('a')
            first_a = a_list[0]
            span = li.find('span')
            if not 'especiais' in first_a['href'] and not 'historias-de-capa' in first_a['href']:
                chapters_list.append(
                    Chapter(
                        id=first_a['href'].split('/')[-1],
                        number=int(span.text.split('.')[0]),
                        title=span.text
                    )
                )
                if len(a_list) > 1:
                    chapters_list.append(
                        Chapter(
                            id=a_list[1]['href'].split('/')[-2],
                            number=int(span.text.split('.')[0]),
                            title=span.text
                        )
                    )
        chapters_list.reverse()
        return chapters_list
    
    def get_chapter_imgs(self, chapter_id):
        response = self.session.get(f'https://onepieceex.net/mangas/leitor/{chapter_id}')
        if not response:
            return False
        pages_dict = json.loads(json.loads(response.text.split('paginasLista = ')[1].split(';')[0]))
        chapter_pages = []
        for url in list(pages_dict.values()):
            chapter_pages.append(
                f'https://onepieceex.net/{url}'
            )
        return chapter_pages
    
    def get_manga_chapters_colored(self) -> list:
        response =  self.session.get('https://onepieceex.net/mangas/')
        if not response:
            return False
        list_chapters = []
        soup = BeautifulSoup(response.text, 'html.parser')
        for a in soup.find_all('a'):
            if a.get('href') == None:
               continue
            if '?v=jump' in a.get('href'):
                list_chapters.append(f'{a['href'].split('/')[-2]}/?v=jump')
        return list_chapters

    def get_all_manga_chapters(self) -> list:
        response =  self.session.get('https://onepieceex.net/mangas/')
        if not response:
            return False
        list_chapters = []
        soup = BeautifulSoup(response.text, 'html.parser')
        next = False
        for a in soup.find_all('a'):
            if a.get('class') == None:
               continue
            if 'online' in a.get('class'):
                if a['href'].split('/')[-3] == 'sbs':
                    continue
                if a['href'].split('/')[-1] == '22' and not next:
                    next = True
                    continue
                if next:
                   list_chapters.append(a['href'].split('/')[-1] if not '?v=jump' in a['href'] else f'{a['href'].split('/')[-2]}/?v=jump')
        return list_chapters

    def get_sbs_chapters(self) -> list:
        response =  self.session.get('https://onepieceex.net/sbs/')
        if not response:
            return False
        sbs_chapters = []
        soup = BeautifulSoup(response.text, 'html.parser')
        for a in soup.find_all('a'):
            if a.get('class') == None:
                continue
            if 'text-uppercase' in a['class']:
                sbs_chapters.append(a['href'].split('/')[-1])
        return sbs_chapters

    def get_chapter_images_url(self, chapter:str, with_base_url:bool=True) -> list:
        response = self.session.get(f'https://onepieceex.net/mangas/leitor/{chapter}')
        if not response:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        url_list = []
        imgs = str(soup.find_all('script')[23]).split(';')[4].split(':')
        imgs.pop(0)
        backslash_char = '\\'
        base_url = 'https://onepieceex.net/mangareader/mangas/' if with_base_url else ''
        chapter = chapter if not '?v=jump' in chapter else f'{chapter.strip('?=vjump')}jump'
        for img in imgs:
            if (
                'png' in img or
                'jpeg' in img or
                'jpg' in img or
                'webp' in img
            ):
                url = [i for i in img.split(backslash_char) if 'png' in i or 'jpg' in i or 'webp' in img or 'jpeg' in img ]
                if len(url) == 0:
                    continue
                url_img = f'''{base_url}{chapter}//{url[0].strip('/')}'''
                url_list.append(
                    url_img
                )
        return url_list
    
    def download_manga_chapter(self, chapter) -> bool:
        response = self.get_chapter_images_url(chapter)
        if not response:
            return False
        path = Path(f'opex/{chapter}')
        path.mkdir(parents=True, exist_ok=True)
        for i, img in enumerate(response):
            page_img = self.session.get(img)
            page_path = Path(f'{path}/{i:04d}.jpg')
            with open(page_path, 'wb') as file:
                for data in page_img.iter_content(1024):
                    file.write(data)
        return True

