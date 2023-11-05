from backend.downloader import *
from backend.interfaces import MangaDl
from backend.manager import ThreadManager
from threading import Thread
from pathlib import Path
import base64
import requests



class Downloader:
    def __init__(self) -> None:
        self.downloaders = {
            'aoashi': AoAshiDl(),
            'gkk': GekkouDl(),
            'md': MangaDexDl(),
            'ms': MangaSeeDl(),
            'ml': MangaLivreDl(),
            'mf': MangaFireDl(),
            'mx': MangaNexusDl(),
            'op': OpScansDl(),
            'opex': OpexDl(),
            'tsct': TaoSectScanDl(),
            'tcb': TCBScansDl()
        }

    def match_source(self, source) -> MangaDl | object:
        return self.downloaders[source.replace('_id', '')]
    
    def search(self, source: str, query: str, pre_results: list[dict] = None):
        source = self.match_source(source)
        if source:
            return source.search(query) if not pre_results \
                else source.search(query, pre_results)
        return False

    def get_chapters(self, source: str, manga_id: str, source_language: str = None) -> list[dict] | list | bool:
        source = self.match_source(source)
        if source:
            try: 
                return source.get_chapters(manga_id) if not source_language \
                    else source.get_chapters(manga_id, source_language)
            except Exception as e: 
                print(e)
        return False

    def get_chapter_image_urls(self, source: str, chapter_id: str) -> list | list[dict] | bool:
        source = self.match_source(source)
        if source:
            return source.get_chapter_imgs(chapter_id)
        return False
    
    def get_base64_images(self, pages: list[str]) -> list[str]:
        images_b64 = []
        threads = ThreadManager()
        def get_base_64_image(url, index: int):
            response = requests.get(url)
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

    
    def download_chapter(self, manga: dict, source: str, chapter: dict) -> bool:
        manga_images = self.get_chapter_image_urls(source, chapter['id'])
        if manga_images:
            threads = ThreadManager()
            def download_page(url, path):
                response = requests.get(url)
                if response and 'image' in response.headers['content-type']:
                        with open(path, 'wb') as file:
                            file.write(response.content)
            folder = Path(f'mangas/{manga["folder_name"]}/{chapter["number"]}')
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
    
    def download_all_chapters(self, manga: dict, source: str, chapters: list[dict]) -> bool:
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
