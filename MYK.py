# why you see this trash project? I believe you can do more.

from bs4 import BeautifulSoup
import csv
from requests import Session
from pathlib import Path

class MangaYouKnow:
    def __init__(self):
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
            
    def get_manga_chapters(self, manga_id):
        chapters_list = []
        offset = 0
        while True:
            response = self.session.get(f'https://mangalivre.net/series/chapters_list.json?page={offset}&id_serie={manga_id}').json()['chapters']
            if not response:
                break
            for chapter in response:
                chapters_list.append(chapter['number'])
            offset += 1
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

    def download_manga_cover(self, url:str):
        manga_id = url.split('/')[-1]
        manga_name = url.split('/')[-2]
        response = self.session.get(f'https://mangalivre.net/manga/{manga_name}/{manga_id}')
        if not response:
            return False
        else:
            soup = BeautifulSoup(response.text, 'html.parser')
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
                manga_path.mkdir(parents = True, exist_ok = True)
                block_size = 1024
                with open(f'{manga_path}/{manga_name}.jpg', 'wb') as file:
                    for data in cover.iter_content(block_size):
                        file.write(data)
                return True
        
    def download_manga_chapter(self, chapter:str, manga_name:str, manga_id:str):
        id_release = MangaYouKnow.get_manga_id_release(chapter, manga_id)

    def download_all_manga_chapters(self):
        pass

    

# userManga = [
#     7,
#     'One Punch Man',
#     'https://mangalivre.net/manga/one-punch-man/1036',
#     '200',
#     'C:/Users/ReiLoko4/Downloads/covers/one.jpg'
# ]

# with open('database/data.csv', 'a+') as file:
#     data = csv.writer(file, lineterminator='\n')
#     data.writerow(userManga)

