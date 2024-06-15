import requests
from bs4 import BeautifulSoup
from backend.interfaces import MangaDl
from backend.managers import ThreadManager
from backend.models import Manga, Chapter
from backend.utilities import conditional_cache_lru, clean_str

class HqNowDl(MangaDl):
    def __init__(self):
        self.base_url = 'https://admin.hq-now.com/graphql'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
            'Accept': '*/*',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://www.hq-now.com/',
            'content-type': 'application/json',
            'Access-Control-Allow-Origin': '*, *',
            'Origin': 'https://www.hq-now.com',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
        })

    @conditional_cache_lru(maxsize=1024)
    def get_cover(self, hq_id: str) -> str:
        response = self.session.post(
            self.base_url,
            json={
                'operationName': 'getHqsById',
                'variables': {'id': hq_id},
                'query': '''query getHqsById($id: Int!) {
                    getHqsById(id: $id) {
                        hqCover
                    }
                }
                '''
            }
        )
        if response.status_code == 200:
            return response.json()['data']['getHqsById'][0]['hqCover']
        return ''

    def search(self, query: str) -> list[Manga] | bool:
        response = self.session.post(
            self.base_url,
            json={
                'operationName': 'getHqsByName',
                'variables': {'name': query},
                'query': '''query getHqsByName($name: String!) {
                    getHqsByName(name: $name) {
                        id
                        name
                    }
                }
                '''
            }
        )
        if response.status_code == 200:
            covers_thr = ThreadManager()
            hqs = []
            for hq in response.json()['data']['getHqsByName']:
                hqs.append(
                    Manga(
                        id=f'{hq['id']}/{clean_str(hq['name'])}',
                        name=hq['name'],
                        folder_name=clean_str(hq['name']),
                        cover='',
                    )
                )
                covers_thr.add_thread_by_args(self.get_cover, (f'{hq['id']}/{clean_str(hq['name'])}',))
            covers_thr.start()
            for hq, cover in zip(hqs, covers_thr.join()):
                hq.cover = cover
            return hqs
        return False
    
    def get_chapters(self, hq_id: str) -> list[Chapter] | bool:
        response = self.session.post(
            self.base_url,
            json={
                'operationName': 'getHqsById',
                'variables': {'id': hq_id},
                'query': '''query getHqsById($id: Int!) {
                    getHqsById(id: $id) {
                        capitulos {
                            id
                            number
                            name
                        }
                    }
                }
                '''
            }
        )
        if response.status_code == 200:
            return [
                Chapter(
                    id=chapter['id'],
                    number=chapter['number'],
                    title=chapter['name'],
                )
                for chapter in response.json()['data']['getHqsById'][0]['capitulos']
            ]
        return False
    
    def get_chapter_imgs(self, chapter_id: str) -> list[str] | bool:
        response = self.session.post(
            self.base_url,
            json={
                'operationName': 'getChapterById',
                'variables': {
                    'chapterId': chapter_id,
                },
                'query': '''query getChapterById($chapterId: Int!) {
                    getChapterById(chapterId: $chapterId) {
                        pictures {      
                            pictureUrl
                        }    
                    }
                }''',
            }
        )
        if response.status_code == 200:
            return [
                picture['pictureUrl'] for picture in
                response.json()['data']['getChapterById']['pictures']
            ]
        return False
    
