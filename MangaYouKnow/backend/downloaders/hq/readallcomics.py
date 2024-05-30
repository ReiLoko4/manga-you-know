import requests
from bs4 import BeautifulSoup
from backend.interfaces import MangaDl
from backend.models import Manga, Chapter

class ReadAllComics(MangaDl):
    def __init__(self):
        self.base_url = 'https://www.hq-now.com'
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

    def search(self, query: str) -> list[Manga] | bool:
        response = self.session.post(
            'https://admin.hq-now.com/graphql',
            json={
                'operationName': 'getHqsByName',
                'variables': {'name': query},
                'query': '''query getHqsByName($name: String!) {
                    getHqsByName(name: $name) {
                        id
                        name
                        editoraId
                        status
                        publisherName
                        impressionsCount
                    }
                }
                '''
            }
        )
        if response.status_code == 200:
            mangas = []
            for manga in response.json()['data']['getHqsByName']:
                mangas.append(
                    Manga(
                        id=manga['id'],
                        name=manga['name'],
                        folder_name=manga['folder_name'],
                        extra_name=manga['extra_name'],
                        author=manga['author'],
                        cover=manga['cover'],
                        grade=0.0
                    )
                )
            return mangas
        return False
    
