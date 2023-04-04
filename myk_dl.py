# why you see this trash project? I believe you can do more.

from bs4 import BeautifulSoup
from customtkinter import *
from requests import Session
from pathlib import Path
from threading import Thread
from unidecode import unidecode
from myk_db import MangaYouKnowDB

class MangaYouKnowDl:
    def __init__(self):
        self.connection_data = MangaYouKnowDB()
        self.session = Session()
        self.session.headers.update({
            'authority': 'mangalivre.net',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'sec-ch-ua': '"Not=A?Brand";v="8", "Chromium";v="110", "Opera GX";v="96"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 OPR/96.0.0.0',
            'x-requested-with': 'XMLHttpRequest',
        })
            
    def get_manga_chapters(self, manga_id:str, manga_name:str):
        manga_name = manga_name.replace(' ', '-').lower()
        chapters_list = []
        offset = 0
        while True:
            response = self.session.get(f'https://mangalivre.net/series/chapters_list.json?page={offset}&id_serie={manga_id}').json()['chapters']
            if not response:
                break
            for chapter in response:
                if chapter['number'] not in chapters_list:
                    chapters_list.append(chapter['number'])
            offset += 1
        add_to_data = Thread(target=self.connection_data.add_data_chapters_txt(chapters_list, manga_name))
        add_to_data.start()
        return chapters_list
    
    def get_manga_id_release(self, chapter_num:str, manga_id:str):
        offset = 0
        while True:
            response = self.session.get(f'https://mangalivre.net/series/chapters_list.json?page={offset}&id_serie={manga_id}').json()['chapters']
            if not response:
                return False
            for chapter in response:
                if chapter_num == chapter['number']:
                    key_scan = list(chapter['releases'].keys())[0]
                    return chapter['releases'][key_scan]['id_release']
            offset +=1

    def save_manga_info(self, manga_name:str, manga_id:str, last_read:str) -> BooleanVar:
        manga_name = manga_name.replace(' ', '-').lower()
        manga_id = str(manga_id)
        response = self.session.get(f'https://mangalivre.net/manga/{manga_name}/{manga_id}')
        if not response:
            return False
        else:
            # create a list to send to data.csv all manga if covers is downloaded
            manga_bd = []
            manga_bd.append(manga_id)
            soup = BeautifulSoup(response.text, 'html.parser')
            h1_tags = soup.find_all('h1')
            nome = str(h1_tags[-1])
            nome = nome.replace('<h1>', '')
            nome = nome.replace('</h1>', '')
            nome = unidecode(nome)
            manga_bd.append(nome)
            manga_bd.append(last_read)
            manga_path = Path(f'Mangas/{manga_name}/cover/{manga_name}.jpg')
            if not manga_path.exists():
                return False
            manga_bd.append(manga_path)
            self.connection_data.add_manga(manga_bd)
            return True
            

    def download_manga_cover(self, manga_name:str, manga_id:str) -> any:
        manga_name = manga_name.replace(' ', '-').lower()
        manga_id = str(manga_id)
        response = self.session.get(f'https://mangalivre.net/manga/{manga_name}/{manga_id}')
        if not response:
            return False
        else:
            # create a list to send to data.csv all manga if covers is downloaded
            soup = BeautifulSoup(response.text, 'html.parser')
            h1_tags = soup.find_all('h1')
            manga_name_from_site = str(h1_tags[-1])
            manga_name_from_site = manga_name_from_site.replace('<h1>', '')
            manga_name_from_site = manga_name_from_site.replace('</h1>', '')
            tags_img = soup.find_all('img')
            cover_url = ''
            for img in tags_img:
                if manga_id in img['src']:
                    if not 'thumb' in img['src']:
                        cover_url = img['src']
                        break
            cover = self.session.get(cover_url)
            if not cover:
                return False
            else:
                manga_path = Path(f'Mangas/{manga_name}/cover')
                manga_path.mkdir(parents=True, exist_ok=True)
                block_size = 1024
                with open(f'{manga_path}/{manga_name}.jpg', 'wb') as file:
                    for data in cover.iter_content(block_size):
                        file.write(data)
                
                h1_tags = soup.find_all('h1')
                manga_name_from_site = str(h1_tags[-1])
                manga_name_from_site = manga_name_from_site.replace('<h1>', '')
                manga_name_from_site = manga_name_from_site.replace('</h1>', '')
                manga_name_from_site = unidecode(manga_name_from_site)
                manga_info = []
                manga_info.append(Path(f'{manga_path}/{manga_name}.jpg'))
                manga_info.append(manga_name_from_site)
                return manga_info
        
    def download_manga_chapter(self, chapter:str, manga_name:str, manga_id:str,) -> BooleanVar: #progress_bar:CTkProgressBar):
        id_release = MangaYouKnowDl.get_manga_id_release(self, chapter, manga_id)
        manga_name = manga_name.replace(' ', '-').lower()
        if not id_release:
            return False
        response = self.session.get(f'https://mangalivre.net/leitor/pages/{id_release}.json', stream=True).json()['images']
        if not response:
            return False
        block_size = 1024
        for img in response:
            page_number = img['legacy'].split('/')[-1]
            if '_' in page_number: page_number = page_number.split('_')[-1]
            if not page_number.split('.')[-2].isnumeric(): page_number = f'000.{page_number.split(".")[-1]}'
            page_img = self.session.get(img['legacy'])
            chapter_path = Path(f'Mangas/{manga_name}/chapters/{chapter}/')
            chapter_path.mkdir(parents=True, exist_ok=True)
            with open(f'{chapter_path}/{page_number}', 'wb') as file:
                for data in page_img.iter_content(block_size):
                    file.write(data)
        return True


    def download_all_manga_chapters(self):
        pass
