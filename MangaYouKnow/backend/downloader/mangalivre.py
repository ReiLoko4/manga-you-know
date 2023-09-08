import requests
from pathlib import Path
from threading import Thread
from bs4 import BeautifulSoup
from backend.database import DataBase
from backend.thread_manager import ThreadManager
import flet as ft


class MangaLivreDl:
    def __init__(self):
        self.connection_data = DataBase()
        self.session = requests.Session()
        self.session.headers.update({
            'authority': 'mangalivre.net',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'referer': 'https://mangalivre.net',
            'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        })

    def get_manga_chapters(self, manga_id: str, write_data: bool = False) -> list:
        print(f'procurando capitulos {manga_id}')
        chapters_list = []
        self.end = False

        def get_offset_json(this_offset):
            response = self.session.get(
                f'https://mangalivre.net/series/chapters_list.json?page={this_offset}&id_serie={manga_id}',
            )
            if not response.json()['chapters'] or not response:
                self.end = True
                return
            chapters_list.append([response.json()['chapters'], this_offset])

        offset = 0
        threads = ThreadManager()
        while True:
            threads.add_thread(
                Thread(target=lambda offset=offset: get_offset_json(offset))
            )
            if offset % 10 == 0:
                threads.start()
                threads.join()
                threads.delete_all_threads()
                if self.end: break
            offset += 1
        def to_sort(e):
            return e[1]
        chapters_list.sort(key=to_sort)
        to_out_list = []
        for i in chapters_list:
            for chapter in i[0]:
                if i[0] == chapters_list[0]:
                    to_out_list.append(chapter)
                elif chapter['id_chapter'] not in [y['id_chapter'] for y in to_out_list]:
                    to_out_list.append(chapter)
        chapters_list = to_out_list
        if write_data:
            self.connection_data.add_data_chapters(
                self.connection_data.get_manga_info_by_key(manga_id['folder_name'], chapters_list))
        return chapters_list
    
    def get_manga_desc(self, manga_id) -> str | bool:
        response = self.session.get(f'https://mangalivre.net/manga/naoimportante/{manga_id}')
        if not response:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        desc = soup.select_one('.series-desc span')
        return desc.text if desc is not None else False

    def get_manga_id_release(self, chapter: str, manga_id: str) -> str | bool:
        offset = 0
        while True:
            response = self.session.get(
                f'https://mangalivre.net/series/chapters_list.json?page={offset}&id_serie={manga_id}',
            ).json()['chapters']
            if not response:
                return False
            for chapter in response:
                if chapter == chapter['number']:
                    key_scan = list(chapter['releases'].keys())[0]
                    return chapter['releases'][key_scan]['id_release']
            offset += 1

    def get_manga_chapter_imgs(self, id_release) -> dict | bool:
        response = self.session.get(
            f'https://mangalivre.net/leitor/pages/{id_release}.json'
        ).json()['images']
        return response if response else False

    def save_manga_info(self, manga_name: str, manga_id: str, last_read: str) -> bool:
        manga_name = manga_name.replace(' ', '-').lower()
        manga_id = str(manga_id)
        response = self.session.get(
            f'https://mangalivre.net/manga/{manga_name}/{manga_id}',
            headers={'referer': f'https://mangalivre.net/manga/{manga_name}/{manga_id}'}
        )
        if not response:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        h1_tags = soup.find_all('h1')
        nome = str(h1_tags[-1])
        nome = nome.replace('<h1>', '')
        nome = nome.replace('</h1>', '')
        manga_path = Path(f'mangas/{manga_name}/cover/{manga_name}.jpg')
        if not manga_path.exists():
            return False
        manga_bd = []
        manga_bd.append(manga_id)
        manga_bd.append(nome)
        manga_bd.append(last_read)
        manga_bd.append(manga_path)
        self.connection_data.add_manga(manga_bd)
        return True

    def search_mangas(self, entry: str) -> dict:
        try:
            response = self.session.post(
                'https://mangalivre.net/lib/search/series.json',
                timeout=3,
                data={'search': entry},
                headers={'referer': 'mangalivre.net'}
            )
        except requests.exceptions.Timeout:
            print('would not?')
            response = self.session.post(
                'https://leitor.net/lib/search/series.json',
                data={'search': entry},
                headers={
                    'referer': 'leitor.net',
                    'authority': 'leitor.net',
                    'alt-Used': 'leitor.net'
                }
            )
        # leitor.net is a mirror of mangalivre.net
        # if the api from mangalivre.net don't response in 3.5 seconds
        # the api from leitor.net will be used.
        return response.json()['series'] if response and response.json()['series'] else {}

    def download_manga_cover(self, manga_name: str, manga_id: str) -> list | bool:
        """
        tu é idiota
        """
        manga_name = manga_name.replace(' ', '-').lower()
        manga_id = str(manga_id)
        response = self.session.get(
            f'https://mangalivre.net/manga/{manga_name}/{manga_id}',
            headers={'referer': f'https://mangalivre.net/manga/{manga_name}/{manga_id}'}
        )
        if not response:
            return False
        # create a list to send to data.csv all manga if covers is downloaded
        soup = BeautifulSoup(response.text, 'html.parser')
        tags_img = soup.find_all('img')
        cover_url = ''
        for img in tags_img:
            if manga_id in img['src']:
                if not 'thumb' in img['src']:
                    cover_url = img['src']
                    break
        cover = self.session.get(
            cover_url,
            headers={'referer': f'https://mangalivre.net/manga/{manga_name}/{manga_id}'}
        )
        if not cover:
            return False
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

    def download_manga_chapter(self, manga_id: str, id_release: str | dict, progress_bar: ft.ProgressBar = None) -> bool:
        manga_info = self.connection_data.get_manga_info_by_key('ml_id', manga_id)
        if type(id_release) == str:
            chapter_info = self.connection_data.get_chapter_info(manga_id, id_release)
            urls = self.get_manga_chapter_imgs(id_release)
        else:
            chapter_info = id_release
            urls = self.get_manga_chapter_imgs(
                id_release['releases'][list(id_release['releases'].keys())[0]]['id_release'])
        if not urls:
            print(f'capitulo {chapter_info["number"]} com erro!')
            return False
        threads = ThreadManager()
        chapter_path = Path(f'mangas/{manga_info["folder_name"]}/chapters/{chapter_info["number"]}/')
        chapter_path.mkdir(parents=True, exist_ok=True)
        # self.pages_downloaded = 0 | Vou comentar, pois não sei se vai querer usar no futuro
        def download_manga_page(url: str, path: Path):
            page_img = self.session.get(url)
            if len(page_img.content) < 5000: return False
            with open(path, 'wb') as file:
                for data in page_img.iter_content(1024):
                    file.write(data)

        for i, img in enumerate(urls):
            extension = (img['legacy'].split('/')[-1]).split('.')[-1]
            page_num = f'{i:04d}'
            page_path = Path(f'{chapter_path}/{page_num}.{extension}')
            download = Thread(target=lambda url=img['legacy'], path=page_path: download_manga_page(url, path))
            threads.add_thread(download)
        threads.start()
        threads.join()
        if not progress_bar == None:
            progress_bar.value += float(progress_bar.data)
            progress_bar.update()
        print(f'capítulo {chapter_info["number"]} baixado! ')
        return True

    def download_list_of_manga_chapters(self, manga_id, chapters_list: list, simultaneous: int = 5):
        manga_info = self.connection_data.get_manga_info_by_key(manga_id)
        chapters = self.connection_data.get_data_chapters(manga_info['folder_name'])
        threads = ThreadManager()
        errors = 0
        for number in chapters_list:
            if number in [i['number'] for i in chapters]:
                id_release = ''
                for chapter in chapters:
                    if number == chapter['number']:
                        id_release = chapter['releases'][list(chapter['releases'].keys())[0]]['id_release']
                threads.add_thread(
                    Thread(target=lambda chapter=id_release: self.download_manga_chapter(manga_id, chapter)))
            else:
                errors += 1
                print(f'capitulo {number} não encontrado')
            if threads.get_len() == simultaneous or number == chapters_list[-1]:
                threads.start()
                threads.join()
                threads.delete_all_threads()
        return not errors == threads.get_len()

    def download_manga_chapters_in_range(self, manga_name, first_chapter, last_chapter, simultaneous: int) -> bool:
        chapters = self.connection_data.get_data_chapters(manga_name)
        if first_chapter not in [i['number'] for i in chapters] or last_chapter not in [i['number'] for i in chapters]:
            return False
        chapters.reverse()
        list_chapters = []
        in_range = False
        for chapter in chapters:
            if chapter['number'] == first_chapter:
                in_range = True
                list_chapters.append(chapter)
            elif chapter['number'] == last_chapter:
                list_chapters.append(chapter)
                break
            elif in_range:
                list_chapters.append(chapter)
        threads = ThreadManager()
        for chapter in list_chapters:
            threads.add_thread(
                Thread(target=lambda chapter=chapter['id']: self.download_manga_chapter(chapter, manga_name)))
            if threads.get_len() == simultaneous or chapter == list_chapters[-1]:
                threads.start()
                threads.join()
                threads.delete_all_threads()
        return True
        # NEED A FIX

    def download_all_manga_chapters(self, manga_id: str, chapters: dict = None, use_local_data: bool = False, progress_bar: ft.ProgressBar = None, simultaneous: int = 5) -> bool:
        '''
        Download all chapters

        manga_id: manga to download
        use_local_data: download the chapters from the already writed json with chapters
        simultaneous: how many chapters to download in the same time
        '''
        if use_local_data:
            chapters = self.connection_data.get_data_chapters(
                self.connection_data.get_manga_info_by_key('ml_id', manga_id)['folder_name'])
        elif chapters == None:
            chapters = self.get_manga_chapters(manga_id)
        chapters.reverse()
        if not progress_bar == None:
            progress_bar.data = 1 / len(chapters)
        threads = ThreadManager()
        for chapter in chapters:
            download_chapter = Thread(
                target=lambda chapter_in=chapter: self.download_manga_chapter(manga_id, chapter_in) if progress_bar == None else self.download_manga_chapter(manga_id, chapter_in, progress_bar)
            )
            threads.add_thread(download_chapter)
            if threads.get_len() == simultaneous or chapter == chapters[-1]:
                threads.start()
                threads.join()
                threads.delete_all_threads()
        return True
