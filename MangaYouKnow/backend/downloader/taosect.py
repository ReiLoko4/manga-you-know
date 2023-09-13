import requests
from bs4 import BeautifulSoup




class TaoSectScanDl:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'authority': 'taosect.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'referer': 'https://taosect.com/',
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        })


    def search(self, entry:str):
        response = self.session.get(
            'https://taosect.com/',
            params={'s': entry}
        )
        if not response:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for a in soup.find_all('a'):
            if a.get('href') != None:
                if 'projeto' in a['href']:
                    results.append(a['href'])
        return results if len(results) != 0 else False


    def get_manga_chapters(self, manga_id:str):
        '''
        manga_id: the name of the manga with the hyphens
        '''
        response = self.session.get(
            f'https://taosect.com/projeto/{manga_id}'
        )
        if not response:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        chapters = []
        for a in soup.find_all('a'):
            if a.get('href') != None:
                if 'leitor-online' in a['href']:
                    chapters.append(a['href'])
        chapters.pop(0)
        chapters.reverse()
        return chapters


    def get_chapter_img_urls(self, chapter_url):
        if not 'taosect.com' in chapter_url:
            return False
        response = self.session.get(
            chapter_url
        )
        if not response:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        urls = []
        for option in soup.find('select', {'id': 'leitor_pagina_projeto'}).find_all('option'):
            urls.append(option['value'])
        return urls










