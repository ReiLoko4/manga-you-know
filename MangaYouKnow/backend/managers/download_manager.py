import base64
from pathlib import Path
from cachetools import cached, TTLCache
from functools import cache
from requests import Session
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from backend.downloaders import *
from backend.utilities import ThreadWithReturnValue as Thread, Notificator
from backend.interfaces import MangaDl
from backend.models import Manga, Chapter, ChapterDownload
from backend.managers import ThreadManager


class DownloadManager:
    def __init__(self) -> None:
        self.session = Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
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
        self.downloads = {}
        self.notificator = Notificator()

    def __match_source__(self, source: str) -> MangaDl:
        return self.downloaders[source.replace('_id', '')]
    
    @cache
    def search(self, source: str, query: str, pre_results: list[Manga] = None):
        dl = self.__match_source__(source)
        if dl:
            return dl.search(query) if not pre_results \
                else dl.search(query, pre_results)
        return False

    @cached(TTLCache(maxsize=1024, ttl=600))
    def get_chapters(self, source: str, manga_id: str, source_language: str = None) -> list[Chapter] | bool:
        source: MangaDl = self.__match_source__(source)
        if source:
            try: 
                return source.get_chapters(manga_id) if not source_language \
                    else source.get_chapters(manga_id, source_language) 
            except Exception as e: 
                print(e)
        return False

    @cache
    def get_chapter_image_urls(self, source: str, chapter_id: str) -> list[str] | bool:
        dl: MangaDl = self.__match_source__(source)
        if dl:
            try:
                return dl.get_chapter_imgs(chapter_id)
            except Exception as e:
                print(e)
        return False
    
    @cache
    def get_image_content(self, url: str) -> bytes | None:
        response = self.session.get(url)
        if response and 'image' in response.headers['content-type']:
            return response.content
        print(response.status_code, url)
    
    @cache
    def get_base_64_image(self, url: str) -> str | None:
        response = self.get_image_content(url)
        if response:
            return base64.b64encode(response).decode('utf-8')

    def get_base64_images(self, pages: list[str]) -> list[str]:
        threads = ThreadManager()
        for image in pages:
            threads.add_thread(
                Thread(
                    target=self.get_base_64_image,
                    args=[image]
                )
            )
        threads.start()
        return [i for i in threads.join() if i]
    
    def download_chapter(self, manga: dict, source: str, chapter: Chapter, is_a_list: bool = False) -> bool:
        manga_images = self.get_chapter_image_urls(source, chapter.id)
        if manga_images:
            threads = ThreadManager()
            def download_page(url: str, path: Path):
                response = self.get_image_content(url)
                if response:
                    with open(path, 'wb') as file:
                        file.write(response)
                        return
                self.notificator.show(manga['name'], f'Erro ao baixar a página {url}. \nVerifique sua conexão ou integridade do site.')
            folder = Path(f'mangas/{manga['folder_name']}/{chapter.number}')
            folder.mkdir(parents=True, exist_ok=True)
            for i, image in enumerate(manga_images):
                path = folder / f'{i:03d}.png'
                threads.add_thread(
                    Thread(
                        target=download_page,
                        args=[image, path]
                    )
                )
            threads.start()
            threads.join()
            if not is_a_list:
                self.notificator.show(manga['name'], f'Download do capítulo {chapter.number} concluído.')
            return True
        self.notificator.show(manga['name'], f'Erro ao baixar o capítulo {chapter.number}. \nVerifique sua conexão ou integridade do site.')
        return False
    
    def download_all_chapters(self, manga: dict, source: str, chapters: list[Chapter], num: int = 5) -> bool:
        chapters.reverse()
        threads = ThreadManager()
        if not chapters:
            return False
        print(f'downloading {len(chapters)} chapters.')
        for chapter in chapters:
            threads.add_thread(
                Thread(
                    target=self.download_chapter,
                    args=[manga, source, chapter]
                )
            )
        threads.start_and_join_by_num(num)
        self.notificator.show(manga['name'], f'Download de {len(chapters)} capítulos concluído.')
        print('finished.')
        return True
