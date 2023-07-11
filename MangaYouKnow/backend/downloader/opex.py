import requests
from pathlib import Path
from threading import Thread
from bs4 import BeautifulSoup
from backend.database import DataBase
from backend.thread_manager import ThreadManager


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
            if 'online' in a.get('class'):
                if a['href'].split('/')[-1] == '?v=jump':
                    continue
                if a['href'].split('/')[-3] == 'sbs':
                    continue
                if a['href'].split('/')[-1] == '22' and not next:
                    next = True
                    continue
                if next:
                    list_chapters.append(a['href'].split('/')[-1] if 'sbs' not in a['href'] else f'sbs {a["href"].split("/")[-1]}')
        return list_chapters

    def get_sbs_chapters(self) -> list:
        response =  self.session.get('https://onepieceex.net/mangas/')
        if not response:
           return False
        sbs_chapters = []
        soup = BeautifulSoup(response.text, 'html.parser')