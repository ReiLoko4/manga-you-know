import base64
import subprocess
from functools import cache
from pathlib import Path

import py7zr
from backend.anime_downloaders import *
from backend.interfaces import AnimeDl, MangaDl
from backend.managers import ThreadManager
from backend.manga_downloaders import *
from backend.models import Chapter, Episode, Manga
from backend.tables import Favorite
from backend.utilities import Notificator
from cachetools import TTLCache, cached
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class DownloadManager:
    def __init__(self) -> None:
        self.session = Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.manga_downloaders = {
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
        self.anime_downloaders = {
            'av': AnimesVisionDl(),
            'af': AnimeFireDl(),
            'ao': AnimesOnlineDl(),
            'ah': AnimesHouseDl(),
        }
        self.downloads = {}
        self.MPV_DOWNLOAD_URL = 'http://downloads.sourceforge.net/project/mpv-player-windows/release/mpv-0.37.0-x86_64.7z'
        self.notificator = Notificator()

    def __match_source__(self, source: str, fav_type: str = 'manga') -> MangaDl | AnimeDl:
        if fav_type == 'manga':
            return self.manga_downloaders[source]
        return self.anime_downloaders[source]
    
    @cache
    def search(self, source: str, query: str, fav_type: str = 'manga') -> list[Manga] | bool:
        dl = self.__match_source__(source, fav_type)
        if dl:
            return dl.search(query)
        return False

    @cached(TTLCache(maxsize=1024, ttl=580))
    def get_chapters(self, source: str, manga_id: str, source_language: str = None) -> list[Chapter] | bool:
        source: MangaDl = self.__match_source__(source)
        if source:
            try:
                return source.get_chapters(manga_id) if not source_language \
                    else source.get_chapters(manga_id, source_language)
            except Exception as e: 
                print(e)
        return False
    
    @cached(TTLCache(maxsize=1024, ttl=580))
    def get_episodes(self, source: str, anime_id: str) -> list[Chapter] | bool:
        source: AnimeDl = self.__match_source__(source, 'anime')
        if source:
            try:
                return source.get_episodes(anime_id)
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
    def get_episode_url(self, source: str, episode_id: str) -> Episode | list[Episode] | bool:
        dl: AnimeDl = self.__match_source__(source, 'anime')
        if dl:
            try:
                return dl.get_episode_url(episode_id)
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
            threads.add_thread_by_args(
                target=self.get_base_64_image,
                args=[image]
            )
        threads.start()
        return [i for i in threads.join() if i]
    
    def start_video_player(self, url: str, title: str = 'Video sem titulo, igual o Palmeiras', header: str = None, local_folder: Path = Path('.')) -> None:
        return subprocess.Popen([
            local_folder / 'mpv/mpv.exe',
            url,
            # '--http-header-fields="Referer: https://corsair-ah.shop"'
            f'--title={title}',
            '--no-border',
            # '--ontop',
            '--fs',
            f'--http-header-fields="Referer: {header if header else 'https://corsair-ah.shop'}"',
        ], 
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        ).communicate()
    
    def is_mpv_installed(self, output_folder: Path = Path('.')) -> bool:
        return (output_folder / 'mpv/mpv.exe').exists()

    def download_file(self, url: str, output_folder: Path = Path('.')):
        chunk_size = 1024
        file_name = url.split('/')[-1].split('?')[0]
        output_location = output_folder / file_name
        with (
            open(output_location, 'wb') as file,
            self.session.get(
                url,
                stream=True,
            ) as response,
        ):
            for chunk in response.iter_content(chunk_size):
                if chunk:
                    file.write(chunk)

    def download_mpv(self, output_folder: Path = Path('.')):
        file_name = output_folder / 'mpv' / 'mpv.exe'
        if not file_name.exists():
            output_folder.mkdir(exist_ok=True)
            self.download_file(self.MPV_DOWNLOAD_URL, output_folder)
            self.extract_7z(output_folder / 'mpv-0.37.0-x86_64.7z', output_folder / 'mpv')
    
    def download_chapter(self, manga: Favorite, source: str, chapter: Chapter, is_in_list: bool = False) -> bool:
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
            folder = Path(f'mangas/{manga.folder_name}/{chapter.number}')
            folder.mkdir(parents=True, exist_ok=True)
            for i, image in enumerate(manga_images):
                path = folder / f'{i:03d}.png'
                threads.add_thread_by_args(
                    target=download_page,
                    args=[image, path]
                )
            threads.start()
            threads.join()
            if not is_in_list:
                self.notificator.show(manga.name, f'Download do capítulo {chapter.number} concluído.')
            return True
        self.notificator.show(manga.name, f'Erro ao baixar o capítulo {chapter.number}. \nVerifique sua conexão ou integridade do site.')
        return False
    
    def download_all_chapters(self, manga: Favorite, source: str, chapters: list[Chapter], num: int = 5) -> bool:
        chapters.reverse()
        threads = ThreadManager()
        if not chapters:
            return False
        print(f'downloading {len(chapters)} chapters.')
        for chapter in chapters:
            threads.add_thread_by_args(
                target=self.download_chapter,
                args=[manga, source, chapter]
            )
        threads.start_and_join_by_num(num)
        self.notificator.show(manga.name, f'Download de {len(chapters)} capítulos concluído.')
        print('finished.')
        return True
    
    def extract_7z(self, input_file: Path, output_folder: Path):
        output_folder.mkdir(exist_ok=True)
        with py7zr.SevenZipFile(input_file, mode='r') as file:
            file.extractall(path=output_folder)
