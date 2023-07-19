import requests
from pathlib import Path
from threading import Thread
from bs4 import BeautifulSoup
# from backend.database import DataBase
# from backend.thread_manager import ThreadManager



class OpexDl:
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

    def get_manga_chapters(self) -> list:
        response =  self.session.get('https://onepieceex.net/mangas/')
        if not response:
            return False
        list_chapters = []
        soup = BeautifulSoup(response.text, 'html.parser')
        next = False
        for a in soup.find_all('a'):
            if a.get('class') == None:
               continue
            if 'online' in a.get('class') and not 'colorido' in a.get('class'):
                if a['href'].split('/')[-3] == 'sbs':
                    continue
                if a['href'].split('/')[-1] == '?v=jump':
                    continue
                if a['href'].split('/')[-1] == '22' and not next:
                    next = True
                    continue
                if next:
                   list_chapters.append(a['href'].split('/')[-1])
        return list_chapters
    
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
                list_chapters.append(f'{a["href"].split("/")[-2]}/?v=jump')
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
                   list_chapters.append(a['href'].split('/')[-1] if not '?v=jump' in a['href'] else f"{a['href'].split('/')[-2]}/?v=jump")
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
        chapter = chapter if not '?v=jump' in chapter else f'{chapter.strip("?=vjump")}jump'
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

