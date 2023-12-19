import requests
from pathlib import Path
from threading import Thread
from backend.database import DataBase
from backend.interfaces import MangaDl
from backend.models import Manga, Chapter
from backend.managers import ThreadManager


class MangaDexDl(MangaDl):
    def __init__(self):
        self.connection_data = DataBase()
    
    def search(self, entry: str, limit='10') -> list[Manga] | bool:
        response = requests.get(
            f'https://api.mangadex.org/manga?includes[]=cover_art&order[relevance]=desc&contentRating[]=safe&contentRating[]=suggestive&contentRating[]=erotica',
            params={
                'title': entry,
                'limit': limit,
            }
        )
        if not response or not response.json(): 
            return False
        list_chapters = []
        for manga in response.json()['data']:
            id_filename = ''
            for types in manga['relationships']:
                if types['type'] == 'cover_art':
                    id_filename = types['attributes']['fileName']
            title_name = manga['attributes']['title']['en'] if 'en' in manga['attributes']['title'] \
                else manga['attributes']['title'][list(manga['attributes']['title'].keys())[0]]
            list_chapters.append(
                Manga(
                    id=manga['id'],
                    name=title_name,
                    folder_name=manga['id'],
                    extra_name=manga['attributes']['altTitles'],
                    description=manga['attributes']['description'].get('en'),
                    cover=f'https://mangadex.org/covers/{manga['id']}/{id_filename}'
                )
            )
        return list_chapters
    
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
    
    def get_chapters(self, manga_id, language='en', limit=500) -> list[Chapter] | bool:
        offset = 0
        chapters_list = []
        while True:
            response = requests.get(
                f'https://api.mangadex.org/manga/{manga_id}/feed?limit={limit}&translatedLanguage[]={language}&order[chapter]=desc&order[volume]=desc',
                params={'offset':offset}
            )
            if not response:
                break
            if not response.json()['data'] or len(response.json()['data']) == 0:
                break
            if len(chapters_list) >= response.json()['total']:
                break
            for chapter in response.json()['data']:
                chapters_list.append(chapter)
            if len(chapters_list) >= response.json()['total']:
                break
            offset += limit
        formatted_list = []
        for chapter in chapters_list:
            formatted_list.append(
                Chapter(
                    id=chapter['id'],
                    number=chapter['attributes']['chapter'],
                    title=chapter['attributes']['title'],
                )
            )
        return formatted_list
    
    def get_chapter_imgs(self, chapter_id) -> list | bool:
        response = requests.get(
            f'https://api.mangadex.org/at-home/server/{chapter_id}?forcePort443=false',
        )
        if not response: 
            print(response.url)
            return False
        chapter = response.json()
        chapter_imgs = []
        for img in chapter['chapter']['data']:
            chapter_imgs.append(
                f'{chapter['baseUrl']}/data/{chapter['chapter']['hash']}/{img}'
            )
        return chapter_imgs
    
    def download_chapter(self, chapter_id) -> bool:
        urls = self.get_chapter_imgs(chapter_id)
        if not urls: return False
        chapter_info = requests.get(
            f'https://api.mangadex.org/chapter/{chapter_id}?includes[]=scanlation_group&includes[]=manga&includes[]=user'
        )
        if not chapter_info: return False
        chapter_path = Path(f'MangaDex/{chapter_info.json()['data']['attributes']['chapter']}/')
        chapter_path.mkdir(parents=True, exist_ok=True)
        hash = urls['hash']
        def download_manga_page(url: str, path: Path):
            image = requests.get(url)
            if not image: return False
            with open(path, 'wb') as file:
                for data in image.iter_content(1024):
                    file.write(data)
        threads = ThreadManager()
        for i, image in enumerate(urls['data']):
            threads.add_thread(Thread(
                target=lambda url=f'https://uploads.mangadex.org/data/{hash}/{image}', path=f'{chapter_path}/{i:04d}.png': download_manga_page(url, path),
            ))
        threads.start()
        threads.join()
        return True
