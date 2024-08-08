import os
import base64
from io import BytesIO
import subprocess
from pathlib import Path
import concurrent.futures

import py7zr
from PIL import Image
from backend.database import DataBase
from backend.downloaders.hq import *
from backend.downloaders.anime import *
from backend.downloaders.manga import *
from backend.interfaces import AnimeDl, MangaDl
from backend.managers import ThreadManager
from backend.models import Chapter, Episode, Manga
from backend.tables import Favorite
from backend.utilities import (
    Notificator, 
    conditional_cache_lru,
    conditional_cache_ttl
)
from cachetools import TTLCache
from requests import Session
from requests.adapters import HTTPAdapter
from retrying import retry
from urllib3 import PoolManager
from urllib3.util.retry import Retry
from yt_dlp import YoutubeDL


class DownloadManager:
    def __init__(self) -> None:
        self.db = DataBase()
        self.session = Session()
        self.session.headers.update({
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
        })
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        # pool_manager = PoolManager(num_pools=200, maxsize=200, block=True)
        self.manga_downloaders = {
            'aoashi': AoAshiDl(),
            'gkk': GekkouDl(),
            'md': MangaDexDl(),
            'mdj': MangaDojoDl(),
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
        self.hq_downloaders = {
            'rac': ReadAllComicsDl(),
            'hqn': HqNowDl(),
        }
        self.anime_downloaders = {
            'av': AnimesVisionDl(),
            'af': AnimeFireDl(),
            'ao': AnimesOnlineDl(),
            'aon': AnimesOnlineNZDl(),
            'ah': AnimesHouseDl(),
            'oa': OtakuAnimessDl(),
            'go': GoyabuDl(),
            'ba': BetterAnimeDl(),
        }
        self.downloads = {}
        self.MPV_DOWNLOAD_URL = 'http://downloads.sourceforge.net/project/mpv-player-windows/release/mpv-0.37.0-x86_64.7z'
        self.notificator = Notificator()

    @conditional_cache_lru(maxsize=1024)
    def __match_source__(self, source: str, fav_type: str = 'manga') -> MangaDl | AnimeDl:
        if fav_type in ('manga', 'hq'):
            return self.manga_downloaders[source] if source in self.manga_downloaders \
                else self.hq_downloaders[source]
        else:
            return self.anime_downloaders[source]
    
    @retry(stop_max_attempt_number=3, wait_fixed=1000)
    @conditional_cache_lru(maxsize=1024)
    def search(self, source: str, query: str, fav_type: str = 'manga') -> list[Manga] | bool:
        dl = self.__match_source__(source, fav_type)
        if dl:
            response = dl.search(query)
            if response != False:
                return response
            raise Exception('Error while searching.')
        return False

    @retry(stop_max_attempt_number=3, wait_fixed=1000)
    @conditional_cache_ttl(TTLCache(maxsize=1024, ttl=580))
    def get_chapters(self, source: str, manga_id: str, source_language: str = None) -> list[Chapter] | bool:
        source: MangaDl = self.__match_source__(source)
        if source:
            response = source.get_chapters(manga_id) if not source_language \
                else source.get_chapters(manga_id, source_language)
            if response != False:
                return response
            raise Exception('Error while getting chapters.')
        return False
    
    @retry(stop_max_attempt_number=3, wait_fixed=1000)
    @conditional_cache_ttl(TTLCache(maxsize=1024, ttl=580))
    def get_episodes(self, source: str, anime_id: str) -> list[Chapter] | bool:
        source: AnimeDl = self.__match_source__(source, 'anime')
        if source:
            response = source.get_episodes(anime_id)
            if response != False:
                return response
            raise Exception('Error while getting episodes.')
        return False

    @retry(stop_max_attempt_number=3, wait_fixed=1000)
    @conditional_cache_lru(maxsize=1024)
    def get_chapter_image_urls(self, source: str, chapter_id: str) -> list[str] | bool:
        dl: MangaDl = self.__match_source__(source)
        if dl:
            response = dl.get_chapter_imgs(chapter_id)
            if response != False:
                return response
            raise Exception('Error while getting chapter image urls.')
        return False
    
    @retry(stop_max_attempt_number=3, wait_fixed=1000)
    @conditional_cache_lru(maxsize=1024)
    def get_episode_url(self, source: str, episode_id: str) -> Episode | list[Episode] | bool:
        dl: AnimeDl = self.__match_source__(source, 'anime')
        if dl:
            try:
                return dl.get_episode_url(episode_id)
            except Exception as e:
                print(e)
        return False
    
    @retry(stop_max_attempt_number=3, wait_fixed=1000)
    @conditional_cache_lru(maxsize=1024)
    def get_image_content(self, url: str) -> bytes | None:
        response = self.session.get(url)
        if response and 'image' in response.headers['content-type']:
            return response.content
        raise Exception('Error while downloading image.')
    
    @conditional_cache_lru(maxsize=1024)
    def get_base_64_image(self, url: str) -> str | None:
        response = self.get_image_content(url)
        if response:
            return base64.b64encode(response).decode('utf-8')

    @retry(stop_max_attempt_number=3, wait_fixed=1000)
    def get_base64_images(self, pages: list[str]) -> list[str]:
        if not pages:
            return []
        threads = ThreadManager()
        for image in pages:
            threads.add_thread_by_args(
                target=self.get_base_64_image,
                args=[image]
            )
        threads.start()
        if not self.db.get_config()['double-page']:
            return [i for i in threads.join() if i]
        return self.join_base64_images_list(
            [i for i in threads.join() if i]
        )

    
    def join_base64_images(self, base64_image1, base64_image2):
        image_data1 = base64.b64decode(base64_image1)
        image_data2 = base64.b64decode(base64_image2)
        image1 = Image.open(BytesIO(image_data1))
        image2 = Image.open(BytesIO(image_data2))
        new_width = image1.width + image2.width
        new_height = max(image1.height, image2.height)
        new_image = Image.new('RGB', (new_width, new_height))
        new_image.paste(image2, (0, 0))
        new_image.paste(image1, (image2.width, 0))  
        buffered = BytesIO()
        new_image.save(buffered, format='JPEG')
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    def join_base64_images_list(self, base64_images: list[str]) -> list[str]:
        if len(base64_images) == 1:
            return base64_images
        for i, img in enumerate(base64_images[1:], 1):
            if i == len(base64_images):
                break
            img_data1 = base64.b64decode(img)
            img1 = Image.open(BytesIO(img_data1))
            img_data2 = base64.b64decode(base64_images[i + 1])
            img2 = Image.open(BytesIO(img_data2))
            if img1.width > img1.height or \
               img2.width > img2.height:
                continue
            new_img = self.join_base64_images(img, base64_images[i + 1])
            base64_images[i] = new_img
            base64_images.pop(i + 1)
        return base64_images


            
    
    def start_video_player(
            self, 
            url: str, 
            title: str = 'Vídeo sem título, igual o Palmeiras', 
            headers: dict = None,
            cookies: str = None,
            local_folder: Path = Path('.')) -> None:
        if cookies:
            with open(local_folder / 'mpv/cookies.txt', 'w') as file:
                file.write(cookies)
        output = subprocess.Popen([
            local_folder / 'mpv/mpv.exe',
            url,
            f'--title={title}',
            '--no-border',
            # '--ontop',
            # '--save-position-on-quit',
            '--no-resume-playback',
            '--fs',
            '--focus-on-open',
            f'--http-header-fields="{'", "'.join([f'{key}: {value}' for key, value in headers.items()])}"' if headers else '',
            f'--cookies-file="{local_folder / 'mpv/cookies.txt'}"' if cookies else '',
        ], 
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        ).communicate()
        if 'http' not in str(url):
            os.remove(url)
        print(output)
        return
    
    def is_mpv_installed(self, output_folder: Path = Path('.')) -> bool:
        return (output_folder / 'mpv/mpv.exe').exists()

    def extract_7z(self, input_file: Path, output_folder: Path):
        output_folder.mkdir(exist_ok=True)
        with py7zr.SevenZipFile(input_file, mode='r') as file:
            file.extractall(path=output_folder)

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
    
    def download_page(self, url: str, path: Path, manga_name):
        response = self.get_image_content(url)
        if response:
            with open(path, 'wb') as file:
                file.write(response)
                return
        self.notificator.show(manga_name, f'Erro ao baixar a página {url}. \nVerifique sua conexão ou integridade do site.')

    def download_chapter(self, manga: Favorite, chapter: Chapter, is_in_list: bool = False) -> bool:
        manga_images = self.get_chapter_image_urls(manga.source, chapter.id)
        if manga_images:
            folder = Path(f'{self.db.get_config()['download-path']}/{manga.folder_name}/{chapter.number}')
            folder.mkdir(parents=True, exist_ok=True)
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                executor.map(
                    self.download_page, 
                    manga_images, 
                    [folder / f'{i:03d}.png' for i in range(len(manga_images))], 
                    [manga.name] * len(manga_images)
                )
            if not is_in_list:
                self.notificator.show(manga.name, f'Download do capítulo {chapter.number} concluído.')
            return True
        self.notificator.show(manga.name, f'Erro ao baixar o capítulo {chapter.number}. \nVerifique sua conexão ou integridade do site.')
        return False
    
    def download_all_chapters(self, manga: Favorite, chapters: list[Chapter], num: int = 5) -> bool:
        if not chapters:
            self.notificator.show(manga.name, f'Erro ao tentar baixar {len(chapters)} capítulos.')
            return False
        print(f'downloading {len(chapters)} chapters.')
        self.notificator.show(manga.name, f'Baixando {len(chapters)} capítulos...')
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            relatory = executor.map(
                self.download_chapter, 
                [manga] * len(chapters), 
                list(reversed(chapters)), 
                [True] * len(chapters)
            )
        relatory = [i for i in relatory if i]
        self.notificator.show(manga.name, f'Download de {len(chapters)} capítulos concluído.\n{len(chapters) - len(relatory)} capítulos com erro.')
        print('finished.')
        return True
    
    def is_downloaded(self, manga: Favorite, chapter : Chapter) -> bool:
        return Path(f'{self.db.get_config()['download-path']}/{manga.folder_name}/{chapter.number}').exists()

    def is_each_downloaded(self, manga: Favorite, chapters: list[Chapter]) -> list[bool]:
        path_favorite = Path(f'{self.db.get_config()['download-path']}/{manga.folder_name}')
        if path_favorite.exists():
            downloaded_chapters = path_favorite.iterdir()
            chapters_names = [chapter.name for chapter in downloaded_chapters]
            return [str(chapter.number) in chapters_names for chapter in chapters]
        return [False] * len(chapters)

    def download_episode(self, anime: Favorite, chapter: Chapter) -> Path | bool:
        episode = self.get_episode_url(anime.source, chapter.id)
        if not episode:
            return False
        episode = episode[0] if type(episode) == list else episode
        with YoutubeDL(
            {
                'http_headers': episode.headers,
                'outtmpl': f'{anime.folder_name}-{chapter.number}-{episode.label}.mp4',
            }
        ) as ydl:
            ydl.download(episode.url)
        self.notificator.show(anime.name, f'Download do episódio {chapter.number} concluído.')
        return Path(f'{anime.folder_name}-{chapter.number}-{episode.label}.mp4')