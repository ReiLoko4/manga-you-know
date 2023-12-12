import base64
import requests
from pathlib import Path
from threading import Thread
from backend.downloaders import *
from backend.interfaces import MangaDl
from backend.constants import DataType
from backend.models import Manga, Chapter, Data
from backend.managers import ThreadManager, StorageManager


class DownloadManager:
    def __init__(self) -> None:
        self.downloaders = {
            'aoashi': AoAshiDl(),
            'gkk': GekkouDl(),
            'md': MangaDexDl(),
            'ms': MangaSeeDl(),
            'mc': MangasChanDl(),
            'ml': MangaLivreDl(),
            'mf': MangaFireDl(),
            'mx': MangaNexusDl(),
            'op': OpScansDl(),
            'opex': OpexDl(),
            'tsct': TaoSectScanDl(),
            'tcb': TCBScansDl(),
            'lmorg': LermangaOrgDl()
        }
        self.storage = StorageManager()

    def __match_source__(self, source: str) -> MangaDl:
        return self.downloaders[source.replace('_id', '')]
    
    def search(self, source: str, query: str, pre_results: list[Manga] = None):
        search_data = Data(DataType.SEARCH, query, source)
        if not self.storage.is_ten_minutes_old(search_data):
            return self.storage.get_data(search_data)
        dl = self.__match_source__(source)
        if dl:
            search_data.data = dl.search(query) if not pre_results \
                else dl.search(query, pre_results)
            self.storage.add_data(search_data)
            return search_data.data
        return False

    def get_chapters(self, source: str, manga_id: str, source_language: str = None) -> list[Chapter] | bool:
        chapters_data = Data(DataType.CHAPTERS, manga_id, source, language=source_language)
        if not self.storage.is_ten_minutes_old(chapters_data):
            return self.storage.get_data(chapters_data)
        source: MangaDl = self.__match_source__(source)
        if source:
            try: 
                chapters_data.data = source.get_chapters(manga_id) if not source_language \
                    else source.get_chapters(manga_id, source_language) 
                self.storage.add_data(chapters_data)
                return chapters_data.data
            except Exception as e: 
                print(e)
        return False

    def get_chapter_image_urls(self, source: str, chapter_id: str) -> list[str] | bool:
        images_data = Data(DataType.IMAGES, chapter_id, source)
        if not self.storage.is_ten_minutes_old(images_data):
            return self.storage.get_data(images_data)
        dl: MangaDl = self.__match_source__(source)
        if dl:
            images_data.data = dl.get_chapter_imgs(chapter_id)
            self.storage.add_data(images_data)
            return images_data.data
        return False
    
    def get_base64_images(self,  source, chapter_id, pages: list[str],) -> list[str]:
        b64_data = Data(DataType.IMAGES_B64, chapter_id, source)
        if not self.storage.is_ten_minutes_old(b64_data):
            return self.storage.get_data(b64_data)
        images_b64 = []
        threads = ThreadManager()
        def get_base_64_image(url, index: int):
            response = requests.get(url)
            print(response.status_code, url)
            if response and 'image' in response.headers['content-type']:
                images_b64.append([base64.b64encode(response.content).decode('utf-8'), index])
        for i, image in enumerate(pages):
            threads.add_thread(
                Thread(
                    target=get_base_64_image,
                    args=(image, i)
                )
            )
        threads.start()
        threads.join()
        images_b64.sort(key=lambda e: e[1])
        b64_data.data = [i[0] for i in images_b64]
        self.storage.add_data(b64_data)
        return b64_data.data
    
    def download_chapter(self, manga: dict, source: str, chapter: Chapter) -> bool:
        manga_images = self.get_chapter_image_urls(source, chapter.id)
        if manga_images:
            threads = ThreadManager()
            def download_page(url, path):
                response = requests.get(url)
                if response and 'image' in response.headers['content-type']:
                        with open(path, 'wb') as file:
                            file.write(response.content)
            folder = Path(f'mangas/{manga['folder_name']}/{chapter.number}')
            folder.mkdir(parents=True, exist_ok=True)
            for i, image in enumerate(manga_images):
                path = f'{folder}/{i:03d}.png'
                threads.add_thread(
                    Thread(
                        target=download_page,
                        args=[image, path]
                    )
                )
            threads.start()
            threads.join()
            return True
        return False
    
    def download_all_chapters(self, manga: dict, source: str, chapters: list[Chapter]) -> bool:
        chapters.reverse()
        threads = ThreadManager()
        if not chapters:
            return False
        print(f'downloading {len(chapters)} chapters.')
        for i, chapter in enumerate(chapters):
            threads.add_thread(
                Thread(
                    target=self.download_chapter,
                    args=[manga, source, chapter]
                )
            )
            if i % 5 == 0 or i == len(chapters) - 1:
                threads.start()
                threads.join()
                threads = ThreadManager()
        print('finished.')
        return True
