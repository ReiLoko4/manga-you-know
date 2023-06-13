# why you see this trash project? I believe you can do more.

from pathlib import Path
from requests import Session
from threading import Thread
from bs4 import BeautifulSoup
from MangaYouKnow.database import DataBase
from MangaYouKnow.threads import ThreadManager



class MangaLivreDl:
    def __init__(self):
        self.connection_data = DataBase()
        self.session = Session()
        self.session.headers.update({
            'authority': 'mangalivre.net',
            'alt-Used': 'mangalivre.net',
            'connection': 'keep-alive',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'sec-ch-ua': '"Not=A?Brand";v="8", "Chromium";v="110", "Opera GX";v="96"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 OPR/96.0.0.0',
            'x-requested-with': 'XMLHttpRequest'
        })

    def get_manga_chapters(self, manga_id:str, manga_name:str) -> list:
        manga_name = manga_name.replace(' ', '-').lower()
        especial = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '.']
        if [i for i in manga_name] in [i for i in especial]:
            for _ in manga_name:
                manga_name = manga_name.replace([i for i in especial], '')
        chapters_list = []
        offset = 0
        while True:
            try: 
                response = self.session.get(
                    f'https://mangalivre.net/series/chapters_list.json?page={offset}&id_serie={manga_id}',
                    headers={'referer': f'https://mangalivre.net/manga/{manga_name}/{manga_id}'}
                ).json()['chapters']
            except:
                response = self.session.get(
                    f'https://mangalivre.net/series/chapters_list.json?page={offset}&id_serie={manga_id}',
                    headers={'referer': f'https://mangalivre.net/manga/{manga_name}/{manga_id}'}
                ).json()
                response = response['chapters']
            if not response: break
            for chapter in response:
                key_scan = list(chapter['releases'].keys())[0]
                id_release = chapter['releases'][key_scan]['id_release']
                if chapter['number'] not in [i[0] for i in chapters_list]:
                    chapters_list.append([chapter['number'], id_release])
                # if id_release not in [i[1] for i in chapters_list]:
                #     chapters_list.append([chapter['number'], id_release])
            offset += 1
        self.connection_data.add_data_chapters(manga_name, chapters_list)
        return chapters_list
    
    def get_manga_id_release(self, chapter:str, manga_id:str) -> str:
        offset = 0
        while True:
            response = self.session.get(
                f'https://mangalivre.net/series/chapters_list.json?page={offset}&id_serie={manga_id}',
            ).json()['chapters']
            if not response: return False
            for chapter in response:
                if chapter == chapter['number']:
                    key_scan = list(chapter['releases'].keys())[0]
                    return chapter['releases'][key_scan]['id_release']
            offset +=1

    def save_manga_info(self, manga_name:str, manga_id:str, last_read:str) -> bool:
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
        if not manga_path.exists(): return False
        manga_bd = []
        manga_bd.append(manga_id)
        manga_bd.append(nome)
        manga_bd.append(last_read)
        manga_bd.append(manga_path)
        self.connection_data.add_manga(manga_bd)
        return True
    
    def search_mangas(self, entry:str) -> dict:
        response = self.session.post(
            'https://mangalivre.net/lib/search/series.json',
            data={'search':entry},
            headers={'referer':'mangalivre.net'}
        )   
        if not response or not response.json()['series']: return False
        return response.json()['series']

    def download_manga_cover(self, manga_name:str, manga_id:str) -> list:
        """
        tu é idiota
        """
        manga_name = manga_name.replace(' ', '-').lower()
        manga_id = str(manga_id)
        response = self.session.get(
            f'https://mangalivre.net/manga/{manga_name}/{manga_id}',
            headers={'referer': f'https://mangalivre.net/manga/{manga_name}/{manga_id}'}
        )
        if not response: return False
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
        if not cover: return False
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

    def download_manga_chapter(self, chapter:str, manga_name:str) -> bool:
        id_release = self.connection_data.get_chapter_id(manga_name, chapter)
        manga_name = manga_name.replace(' ', '-').lower()
        response = self.session.get(
            f'https://mangalivre.net/leitor/pages/{id_release}.json',
            headers={'referer': f'https://mangalivre.net/ler/{manga_name}/online/{id_release}/{chapter}'}
        ).json()['images']
        if not response:
            print(f'capitulo {chapter} com erro!') 
            return False
        threads = ThreadManager()
        chapter_path = Path(f'mangas/{manga_name}/chapters/{chapter}/')
        chapter_path.mkdir(parents=True, exist_ok=True)
        self.pages_downloaded = 0
        def download_manga_page(url:str, path:Path):
            page_img = self.session.get(url)
            if len(page_img.content) < 5000: return False
            with open(path, 'wb') as file:
                for data in page_img.iter_content(1024):
                    file.write(data)

        for i, img in enumerate(response):
            extension = (img['legacy'].split('/')[-1]).split('.')[-1]
            page_num = f'{i:04d}'
            page_path = Path(f'{chapter_path}/{page_num}.{extension}')
            download = Thread(target=lambda url=img['legacy'], path=page_path: download_manga_page(url, path))
            threads.add_thread(download)
        threads.start()
        threads.join()
        print(f'capítulo {chapter} baixado! ')
        return True
    
    def download_list_of_manga_chapters(self, manga_name, chapters_list:list, simultaneous:int):
        threads = ThreadManager()
        errors = 0
        for chapter in chapters_list:
            try:
                threads.add_thread(Thread(target=lambda chapter=chapter: self.download_manga_chapter(chapter, manga_name)))
                if threads.get_len() == simultaneous or chapter == chapters_list[-1]:
                    threads.start()
                    threads.join()
                    threads.delete_all_threads()
            except:
                print(f'capitulo {chapter} não encontrado')
                errors += 1
        if errors == threads.get_len():
            print('nenhum capitulo encontrado!')
            return False
        return True

    def download_manga_chapters_in_range(self, manga_name, first_chapter, last_chapter, simultaneous:int) -> bool:
        chapters = self.connection_data.get_data_chapters(manga_name)
        if first_chapter not in [i[0] for i in chapters] or last_chapter not in [i[0] for i in chapters]:
            return False
        chapters.reverse()
        list_chapters = []
        in_range = False
        for chapter in chapters:
            if chapter[0] == first_chapter:
                in_range = True
                list_chapters.append(chapter)
            elif chapter[0] == last_chapter:
                list_chapters.append(chapter)
                break
            elif in_range:
                list_chapters.append(chapter)
        threads = ThreadManager()
        for chapter in list_chapters:
            threads.add_thread(Thread(target=lambda chapter=chapter[0]: self.download_manga_chapter(chapter, manga_name)))
            if threads.get_len() == simultaneous or chapter == list_chapters[-1]:
                threads.start()
                threads.join()
                threads.delete_all_threads()
        return True

    def download_all_manga_chapters(self, manga_name:str, simultaneous:int) -> bool:
        '''
        Download all chapters

        manga_name: manga to download
        simultaneous: how many chapters to download in the same time
        '''
        chapters = self.connection_data.get_data_chapters(manga_name)
        chapters.reverse()
        threads = ThreadManager()
        for chapter in chapters:
            download_chapter = Thread(target=lambda chapter=chapter[0]: self.download_manga_chapter(chapter, manga_name))
            threads.add_thread(download_chapter)
            if threads.get_len() == simultaneous or chapter == chapters[-1]:
                threads.start()
                threads.join()
                threads.delete_all_threads()
        return True


class MangaDexDl:
    def __init__(self):
        self.session = Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://mangadex.org/',
            'Origin': 'https://mangadex.org',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
        })
    
    def search_mangas(self, entry:str, limit='5') -> dict | bool:

        # response = self.session.get(
        #     f'https://api.mangadex.org/group?name={entry}&limit={limit}&includes[]=leader'
        # )
        response = self.session.get(
            f'https://api.mangadex.org/manga?title={entry}&limit={limit}&contentRating[]=safe&contentRating[]=suggestive&contentRating[]=erotica&includes[]=cover_art&order[relevance]=desc',
        )
        if not response or not response.json(): 
            return False
        return response.json()
    
    def search_author(self, entry:str, limit=5)-> dict | bool:
        response = self.session.get(
            'https://api.mangadex.org/author',
            params={
                'name': entry,
                'limit': limit
            }
        )
        if not response or not response.json():
            return False
        return response.json()
    
    def get_manga_chapters(self, manga_id, limit=96) -> dict | bool:
        offset = 0
        manga_list = []
        while True:
            response = self.session.get(
                f'https://api.mangadex.org/manga/{manga_id}/feed?limit={limit}&includes[]=scanlation_group&includes[]=user&order[volume]=desc&order[chapter]=desc&offset=0&contentRating[]=safe&contentRating[]=suggestive&contentRating[]=erotica&contentRating[]=pornographic',
                params={'offset':offset}
            )
            if not response:
                break
            for chapter in response.json()['data']:
                manga_list.append([chapter['id'], chapter['attributes']['chapter'] ])
            print(offset)
            offset += 1
        if len(manga_list) == 0: return False 
        return manga_list
    

class GekkouDl:
    def __init__(self):
        self.session = Session()
        self.session.headers.update({
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'x-requested-with': 'XMLHttpRequest',
            'origin': 'https://gekkou.com.br',
            'alt-used': 'gekkou.com.br',
            'connection': 'keep-alive',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',

        })

    def search_mangas(self, entry:str) -> dict | bool:
        entry.replace(' ', '+')
        response = self.session.get(
            'https://gekkou.com.br/wp-admin/admin-ajax.php',
            data = {
                'action': 'wp-manga-search-manga',
                'title': entry
            }
        )
        if not response:
            return False
        return response.json()

    def get_chapters(self, manga_name):
        response = self.session.post(f'https://gekkou.com.br/manga/{manga_name}/ajax/chapters/')
        if not response:
            return False
        return response
        # don't works


class OpexDl:
    def __init__(self):
        pass