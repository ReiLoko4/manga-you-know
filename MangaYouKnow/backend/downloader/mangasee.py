from requests import Session
from backend.interfaces import MangaDl
from backend.models import Manga, Chapter
import json


class MangaSeeDl(MangaDl):
    def __init__(self) -> None:
        self.session = Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Alt-Used': 'www.mangasee123.com',
            'Connection': 'keep-alive',
            'Referer': 'https://www.mangasee123.com',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
        })

    def search(self, query: str, pre_results: list[dict] = None):
        if not pre_results:
            response = self.session.get('https://www.mangasee123.com/search?name=qualquercoisaliteralmente')
            if response.status_code != 200:
                return False
            results = json.loads(response.text.split('vm.Directory = ')[1].split('\n')[0][:-2])
            mangas = []
            for manga in results:
                mangas.append(
                    Manga(
                        id=manga['i'],
                        name=manga['s'],
                        folder_name=manga['i'],
                        extra_name=manga['al'],
                        author=manga['a'],
                        cover=f'https://temp.compsci88.com/cover/{manga['i']}.jpg',
                        grade=0.0
                    )
                )
        if pre_results:
            mangas = pre_results
        final_result = []
        for manga in mangas:
            manga.grade = 0.0
            if query.lower() in manga.name.lower():
                manga.grade += 1
            if [i for i in manga.extra_name if query.lower() in i.lower()]:
                manga.grade += 1
            if [i for i in manga.author if query.lower() in i.lower()]:
                manga.grade += 0.5
            if manga.grade > 0:
                final_result.append(manga)
        final_result.sort(key=lambda x: x.grade, reverse=True)
        return [final_result[:10], mangas]
    
    def get_chapters(self, manga_id: str):
        response = self.session.get(f'https://www.mangasee123.com/manga/{manga_id}')
        if response.status_code == 200:
            results = json.loads(response.text.split('vm.Chapters = ')[1].split('\n')[0][:-2])
            page = response.text.split('vm.PageOne="')[1].split('"')[0]
            chapters = []
            for chapter in results:
                index = ''
                if int(chapter['Chapter'][0]) != 1:
                    index = f'-index-{chapter['Chapter'][0]}'
                chapters.append(
                    Chapter(
                        id=f'{manga_id}-chapter-{int(chapter['Chapter'][1:-1])}{index}{page}.html',
                        number=int(chapter['Chapter'][1:-1]),
                        title=chapter['ChapterName'],
                    )
                )
            return chapters
        return False

    def get_chapter_imgs(self, chapter_id: str):
        response = self.session.get(f'https://mangasee123.com/read-online/{chapter_id}')
        if response.status_code == 200:
            dominy = response.text.split('vm.CurPathName = "')[1].split('"')[0]
            manga_id = response.text.split('vm.IndexName = "')[1].split('"')[0]
            manga_info = json.loads(response.text.split('vm.CurChapter = ')[1].split('\n')[0][:-2])
            directory = manga_info['Directory']
            num_pages = int(manga_info['Page'])
            chapter = manga_info['Chapter'][1:-1]
            chapter_imgs = []
            for page in range(1, num_pages+1, 1):
                num = f'{page:03d}'
                chapter_imgs.append(
                    f'https://{dominy}/manga/{manga_id}/{directory}/{chapter}-{num}.png'
                )
            return chapter_imgs
        return False

# print(MangaSeeDl().search('one piece'))