# why you see this trash project? I believe you can do more.

from pathlib import Path
from customtkinter import *
from requests import Session
from threading import Thread
from bs4 import BeautifulSoup
from myk_db import MangaYouKnowDB
from myk_thread import ThreadManager



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

    def get_manga_chapters(self, manga_id:str, manga_name:str) -> list:
        manga_name = manga_name.replace(' ', '-').lower()
        especial = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '.']
        if [i for i in manga_name] in [i for i in especial]:
            for _ in manga_name:
                manga_name = manga_name.replace([i for i in especial], '')
        chapters_list = []
        offset = 0
        while True:
            try: response = self.session.get(f'https://mangalivre.net/series/chapters_list.json?page={offset}&id_serie={manga_id}').json()['chapters']
            except: 
                response = self.session.get(f'https://mangalivre.net/series/chapters_list.json?page={offset}&id_serie={manga_id}').json()['chapters']
            if not response: break
            for chapter in response:
                key_scan = list(chapter['releases'].keys())[0]
                id_release = chapter['releases'][key_scan]['id_release']
                if chapter['number'] not in [i[0] for i in chapters_list]:
                    chapters_list.append([chapter['number'], id_release])
                # if id_release not in [i[1] for i in chapters_list]:
                #     chapters_list.append([chapter['number'], id_release])
            offset += 1
        self.connection_data.add_data_chapters(manga_name, chapters_list)
        return chapters_list
    
    
    def get_manga_id_release(self, chapter:str, manga_id:str) -> str:
        offset = 0
        while True:
            response = self.session.get(f'https://mangalivre.net/series/chapters_list.json?page={offset}&id_serie={manga_id}').json()['chapters']
            if not response: return False
            for chapter in response:
                if chapter == chapter['number']:
                    key_scan = list(chapter['releases'].keys())[0]
                    return chapter['releases'][key_scan]['id_release']
            offset +=1

    def save_manga_info(self, manga_name:str, manga_id:str, last_read:str) -> bool:
        manga_name = manga_name.replace(' ', '-').lower()
        manga_id = str(manga_id)
        response = self.session.get(f'https://mangalivre.net/manga/{manga_name}/{manga_id}')
        if not response:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        h1_tags = soup.find_all('h1')
        nome = str(h1_tags[-1])
        nome = nome.replace('<h1>', '')
        nome = nome.replace('</h1>', '')
        manga_path = Path(f'mangas/{manga_name}/cover/{manga_name}.jpg')
        if not manga_path.exists(): return False
        manga_bd = []
        manga_bd.append(manga_id)
        manga_bd.append(nome)
        manga_bd.append(last_read)
        manga_bd.append(manga_path)
        self.connection_data.add_manga(manga_bd)
        return True
    
    def download_manga_cover(self, manga_name:str, manga_id:str) -> list:
        """
        tu é idiota
        """
        manga_name = manga_name.replace(' ', '-').lower()
        manga_id = str(manga_id)
        response = self.session.get(f'https://mangalivre.net/manga/{manga_name}/{manga_id}')
        if not response: return False
        # create a list to send to data.csv all manga if covers is downloaded
        soup = BeautifulSoup(response.text, 'html.parser')
        tags_img = soup.find_all('img')
        cover_url = ''
        for img in tags_img:
            if manga_id in img['src']:
                if not 'thumb' in img['src']:
                    cover_url = img['src']
                    break
        cover = self.session.get(cover_url)
        if not cover: return False
        manga_path = Path(f'mangas/{manga_name}/cover')
        manga_path.mkdir(parents=True, exist_ok=True)
        with open(f'{manga_path}/{manga_name}.jpg', 'wb') as file:
            for data in cover.iter_content(1024):
                file.write(data)
        h1_tags = soup.find_all('h1')
        manga_name_from_site = str(h1_tags[-1])
        manga_name_from_site = manga_name_from_site.replace('<h1>', '')
        manga_name_from_site = manga_name_from_site.replace('</h1>', '')
        return [Path(f'{manga_path}/{manga_name}.jpg'), manga_name_from_site]

    def download_manga_page(self, url:str, path:Path):
        page_img = self.session.get(url)
        with open(path, 'wb') as file:
            for data in page_img.iter_content(1024):
                file.write(data)


    def download_manga_chapter(self, chapter:str, manga_name:str) -> bool:
        id_release = self.connection_data.get_chapter_id(manga_name, chapter)
        manga_name = manga_name.replace(' ', '-').lower()
        response = self.session.get(f'https://mangalivre.net/leitor/pages/{id_release}.json', stream=True).json()['images']
        if not response: return False
        threads = ThreadManager()
        chapter_path = Path(f'mangas/{manga_name}/chapters/{chapter}/')
        chapter_path.mkdir(parents=True, exist_ok=True)
        for i, img in enumerate(response):
            extension = (img['legacy'].split('/')[-1]).split('.')[-1]
            page_num = f'{i:04d}'
            page_path = Path(f'{chapter_path}/{page_num}.{extension}')
            download = Thread(target=lambda url=img['legacy'], path=page_path: self.download_manga_page(url, path))
            threads.add_thread(download)
        threads.start()
        threads.join()
        print(f'capítulo {chapter} baixado! ')
        return True
    
    def download_all_manga_chapters(self, manga_name:str, simultaneous:int) -> bool:
        chapters = self.connection_data.get_data_chapters(manga_name)
        threads = ThreadManager()
        for chapter in chapters:
            download_chapter = Thread(target=lambda chapter=chapter, name=manga_name: self.download_manga_chapter(chapter, name))
            threads.add_thread(download_chapter)
            if threads.get_len() == simultaneous:
                threads.start()
                threads.join()
                threads.delete_all_threads()
        return True
    