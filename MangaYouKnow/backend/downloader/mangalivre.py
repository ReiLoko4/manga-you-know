import asyncio
from pathlib import Path

import requests
from backend.database import DataBase
from bs4 import BeautifulSoup
from httpx import AsyncClient


async def start_session():
    return AsyncClient()


class MangaLivreDl:
    def __init__(self):
        self.session = None
        self.connection_data = DataBase()

        self.session = asyncio.run(start_session())

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

    async def get_manga_chapters(self, manga_id: str, write_data: bool = False) -> list:
        if self.session is None:
            await start_session()
        print(f'procurando capitulos {manga_id}')
        chapters_list = []

        async def get_offset_json(this_offset) -> dict:
            # response = self.session.get(
            #     f'https://mangalivre.net/series/chapters_list.json?page={this_offset}&id_serie={manga_id}',
            # )
            response = await self.session.get(
                f'https://leitor.net/series/chapters_list.json?page={this_offset}&id_serie={manga_id}',
            )
            if not response.json()['chapters'] or not response:
                return {}
            return response.json()['chapters']

        offset = 0
        while True:
            chapter_data = await get_offset_json(offset)
            if offset % 10 == 0:
                if not chapter_data:
                    break
            chapters_list.insert(offset, chapter_data)
            offset += 1
        to_out_list = []
        for i in chapters_list:
            for chapter in i:
                to_out_list.append(chapter)
        chapters_list = to_out_list
        final_list = []
        for i, chapter in enumerate(chapters_list):
            if i == 0:
                final_list.append(chapter)
            elif chapter['id_chapter'] not in [y['id_chapter'] for y in final_list]:
                final_list.append(chapter)
        chapters_list = final_list

        def to_sort(e):
            number = str(e['number'])
            number = number.replace(',', '.')
            return float(number)

        chapters_list.sort(key=to_sort, reverse=True)
        if write_data:
            self.connection_data.add_data_chapters(
                self.connection_data.get_manga_info(manga_id['folder_name'], chapters_list))
        return chapters_list

    async def get_manga_desc(self, manga_id) -> str | bool:
        if self.session is None:
            await start_session()
        response = await self.session.get(f'https://mangalivre.net/manga/naoimportante/{manga_id}')
        if not response:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        desc = soup.select_one('.series-desc span')
        return desc.text if desc is not None else False

    async def get_manga_id_release(self, chapter: str, manga_id: str) -> str | bool:
        if self.session is None:
            await start_session()
        offset = 0
        while True:
            response = await self.session.get(
                f'https://mangalivre.net/series/chapters_list.json?page={offset}&id_serie={manga_id}',
            )
            response = response.json()['chapters']
            if not response:
                return False
            for chapter in response:
                if chapter == chapter['number']:
                    key_scan = list(chapter['releases'].keys())[0]
                    return chapter['releases'][key_scan]['id_release']
            offset += 1

    async def get_manga_chapter_imgs(self, id_release) -> dict | bool:
        if self.session is None:
            await start_session()
        response = await self.session.get(
            f'https://mangalivre.net/leitor/pages/{id_release}.json'
        )
        return response.json()['images'] if response and response.json()['images'] else False

    async def save_manga_info(self, manga_name: str, manga_id: str, last_read: str) -> bool:
        if self.session is None:
            await start_session()
        manga_name = manga_name.replace(' ', '-').lower()
        manga_id = str(manga_id)
        response = await self.session.get(
            f'https://mangalivre.net/manga/{manga_name}/{manga_id}',
            headers={'referer': f'https://mangalivre.net/manga/{manga_name}/{manga_id}'}
        )
        if not response.status_code == 200:
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

    async def search_mangas(self, entry: str) -> dict:
        if self.session is None:
            await start_session()
        try:
            if self.session.is_closed:
                return []
            response = await self.session.post(
                'https://mangalivre.net/lib/search/series.json',
                timeout=3,
                data={'search': entry.lower()},
                headers={'referer': 'mangalivre.net'}
            )
        except requests.exceptions.Timeout:
            print('would not?')
            response = await self.session.post(
                'https://leitor.net/lib/search/series.json',
                data={'search': entry.lower()},
                headers={
                    'referer': 'leitor.net',
                    'authority': 'leitor.net',
                    'alt-Used': 'leitor.net'
                }
            )
        # leitor.net is a mirror of mangalivre.net
        # if the api from mangalivre.net don't response in 3.5 seconds
        # the api from leitor.net will be used.
        return response.json()['series'] if response and response.json()['series'] else False

    async def download_manga_cover(self, manga_name: str, manga_id: str) -> list | bool:
        """
        tu é idiota
        Que é isso, rapaz
        """
        if self.session is None:
            await start_session()
        manga_name = manga_name.replace(' ', '-').lower()
        manga_id = str(manga_id)
        response = await self.session.get(
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
        cover = await self.session.get(
            cover_url,
            headers={'referer': f'https://mangalivre.net/manga/{manga_name}/{manga_id}'}
        )
        if not cover:
            return False
        manga_path = Path(f'mangas/{manga_name}/cover')
        manga_path.mkdir(parents=True, exist_ok=True)
        with open(f'{manga_path}/{manga_name}.jpg', 'wb') as file:
            for data in cover.iter_bytes(1024):
                file.write(data)
        h1_tags = soup.find_all('h1')
        manga_name_from_site = str(h1_tags[-1])
        manga_name_from_site = manga_name_from_site.replace('<h1>', '')
        manga_name_from_site = manga_name_from_site.replace('</h1>', '')
        return [Path(f'{manga_path}/{manga_name}.jpg'), manga_name_from_site]

    async def download_manga_chapter(self, manga_id: str, id_release: str | dict) -> bool:
        if self.session is None:
            await start_session()
        manga_info = self.connection_data.get_manga_info(manga_id)

        if type(id_release) == str:
            chapter_info = self.connection_data.get_chapter_info(manga_id, id_release)
            urls = await self.get_manga_chapter_imgs(id_release)
        else:
            chapter_info = id_release
            urls = await self.get_manga_chapter_imgs(
                id_release['releases'][list(id_release['releases'].keys())[0]]['id_release'])
        if not urls:
            print(f'capitulo {chapter_info["number"]} com erro!')
            return False
        chapter_path = Path(f'mangas/{manga_info["folder_name"]}/chapters/{chapter_info["number"]}/')
        chapter_path.mkdir(parents=True, exist_ok=True)
        self.pages_downloaded = 0

        async def download_manga_page(url: str, path: Path):
            page_img = await self.session.get(url)
            if len(page_img.content) < 5000:
                return False
            with open(path, 'wb') as file:
                for data in page_img.iter_bytes(1024):
                    file.write(data)

        tasks = []

        for i, img in enumerate(urls):
            extension = (img['legacy'].split('/')[-1]).split('.')[-1]
            page_num = f'{i:04d}'
            page_path = Path(f'{chapter_path}/{page_num}.{extension}')
            download = await download_manga_page(img['legacy'], page_path)
            tasks.append(download)

        await asyncio.gather(*tasks)
        print(f'capítulo {chapter_info["number"]} baixado! ')
        return True

    async def download_list_of_manga_chapters(self, manga_id, chapters_list: list, simultaneous: int = 5):
        if self.session is None:
            await start_session()
        manga_info = self.connection_data.get_manga_info(manga_id)
        chapters = self.connection_data.get_data_chapters(manga_info['folder_name'])
        errors = 0
        tasks = []
        for number in chapters_list:
            if number in [i['number'] for i in chapters]:
                id_release = ''
                for chapter in chapters:
                    if number == chapter['number']:
                        id_release = chapter['releases'][list(chapter['releases'].keys())[0]]['id_release']
                download = await self.download_manga_chapter(manga_id, id_release)
                tasks.append(download)
            else:
                errors += 1
                print(f'capitulo {number} não encontrado')

        if errors == len(tasks):
            print('Nenhum capitulo encontrado!')
            return False
        await asyncio.gather(*tasks)
        return True

    async def download_manga_chapters_in_range(self, manga_name, first_chapter, last_chapter,
                                               simultaneous: int) -> bool:
        if self.session is None:
            await start_session()
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
        tasks = []
        for chapter in list_chapters:
            download = await self.download_manga_chapter(chapter['id'], manga_name)
            tasks.append(download)
        await asyncio.gather(*tasks)
        return True
        # NEED A FIX

    async def download_all_manga_chapters(self, manga_id: str, use_local_data: bool = False,
                                          simultaneous: int = 5) -> bool:
        if self.session is None:
            await start_session()
        '''
        Download all chapters

        manga_id: manga to download
        use_local_data: download the chapters from the already writed json with chapters
        simultaneous: how many chapters to download in the same time
        '''
        if use_local_data:
            chapters = self.connection_data.get_data_chapters(
                self.connection_data.get_manga_info(manga_id)['folder_name'])
        else:
            chapters = await self.get_manga_chapters(manga_id)
        chapters.reverse()

        tasks = [self.download_manga_chapter(manga_id, chapter) for chapter in chapters]
        await asyncio.gather(*tasks)
        return True

    async def close_session(self):
        await self.session.aclose()
