import base64
import requests
from pathlib import Path
from threading import Thread
from backend.downloader import *
from backend.interfaces import MangaDl
from backend.manager import ThreadManager
from backend.models import Manga, Chapter



class Downloader:
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

    def __match_source__(self, source: str) -> MangaDl:
        return self.downloaders[source.replace('_id', '')]
    
    def search(self, source: str, query: str, pre_results: list[Manga] = None):
        dl = self.__match_source__(source)
        if dl:
            return dl.search(query) if not pre_results \
                else dl.search(query, pre_results)
        return False

    def get_chapters(self, dl: str, manga_id: str, source_language: str = None) -> list[Chapter] | bool:
        dl: MangaDl = self.__match_source__(dl)
        if dl:
            try: 
                return dl.get_chapters(manga_id) if not source_language \
                    else dl.get_chapters(manga_id, source_language)
            except Exception as e: 
                print(e)
        return False

    def get_chapter_image_urls(self, source: str, chapter_id: str) -> list[str] | bool:
        dl: MangaDl = self.__match_source__(source)
        if dl:
            return dl.get_chapter_imgs(chapter_id)
        return False
    
    def get_base64_images(self, pages: list[str]) -> list[str]:
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
        return [i[0] for i in images_b64]

    
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
