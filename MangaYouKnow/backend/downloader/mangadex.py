import requests
from pathlib import Path
from threading import Thread
from bs4 import BeautifulSoup
from backend.database import DataBase
from backend.thread_manager import ThreadManager


class MangaDexDl:
    def __init__(self):
        self.connection_data = DataBase()
    
    def search_mangas(self, entry:str, limit='5') -> dict | bool:
        response = requests.get(
            f'https://api.mangadex.org/manga',
            params={
                'title': entry,
                'limit': limit    
            }
        )
        if not response or not response.json(): 
            return False
        return response.json()
    
    def search_author(self, entry:str, limit=5)-> dict | bool:
        response = requests.get(
            'https://api.mangadex.org/author',
            params={
                'name': entry,
                'limit': limit
            }
        )
        if not response or not response.json():
            return False
        return response.json()
    
    def get_manga_chapters(self, manga_id, limit=500) -> dict | bool:
        offset = 0
        manga_list = []
        while True:
            response = requests.get(
                f'https://api.mangadex.org/manga/{manga_id}/feed?limit={limit}&translatedLanguage[]=pt-br&order[chapter]=desc&order[volume]=desc',
                params={'offset':offset}
            )
            if not response:
                break
            if not response.json()['data'] or len(response.json()['data']) == 0:
                break
            if len(manga_list) >= response.json()['total']:
                break
            for chapter in response.json()['data']:
                manga_list.append(chapter)
            if len(manga_list) >= response.json()['total']:
                break
            offset += limit
        self.connection_data.add_data_chapters('one piece', manga_list)
        return manga_list
    
    def get_chapters_image_urls(self, chapter_id) -> list | bool:
        response = requests.get(
            f'https://api.mangadex.org/at-home/server/{chapter_id}?forcePort443=false',
        )
        if not response: return False
        return response.json()['chapter']
    
    def download_chapter(self, chapter_id) -> bool:
        urls = self.get_chapters_image_urls(chapter_id)
        if not urls: return False
        chapter_info = self.session.get(
            f'https://api.mangadex.org/chapter/{chapter_id}?includes[]=scanlation_group&includes[]=manga&includes[]=user'
        )
        if not chapter_info: return False
        chapter_path = Path(f'MangaDex/{chapter_info.json()["data"]["attributes"]["chapter"]}/')
        chapter_path.mkdir(parents=True, exist_ok=True)
        hash = urls['hash']
        for i, image in enumerate(urls['data']):
            response = self.session.get(f'https://uploads.mangadex.org/data/{hash}/{image}')
            if not image: return False
            with open(f'{chapter_path}/{i:04d}.png', 'wb') as file:
                for data in response.iter_content(1024):
                    file.write(data)
        return True
    