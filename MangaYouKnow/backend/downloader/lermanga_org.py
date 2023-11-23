from requests import Session, get
from bs4 import BeautifulSoup
from backend.interfaces import MangaDl
from backend.models import Manga, Chapter


class LermangaOrgDl(MangaDl):
    def __init__(self):
        self.session = Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://lermanga.org/',
            'Alt-Used': 'lermanga.org',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
        })

    def search(self, query: str) -> list[Manga] | bool:
        response = self.session.get(f'https://lermanga.org/?s={query.replace(' ', '+')}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            mangas = []
            for div in soup.find_all('div', {'class': 'flw-item'}):
                a = div.find('a', {'data-jname': True})
                mangas.append(
                    Manga(
                        id=a['href'].split('/')[-2],
                        name=a.text,
                        folder_name=a['href'].split('/')[-2],
                        cover=div.find('img')['src']
                    )
                )
            return mangas[:10]
        return False
            
    def get_chapters(self, manga_id: str) -> list[Chapter] | bool:
        response = self.session.get(f'https://lermanga.org/mangas/{manga_id}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            chapters = []
            for a in soup.find('div', {'class': 'manga-chapters'}).find_all('a'):
                chapters.append(
                    Chapter(
                        id=a['href'].split('/')[-2],
                        number=a['href'].split('/')[-2].split('-')[-1],
                        title=a.text
                    )
                )
            return chapters
        return False
    
    def get_chapter_imgs(self, chapter_id: str) -> list[str] | bool:
        response = self.session.get(f'https://lermanga.org/capitulos/{chapter_id}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            pages = []
            chpt_split = chapter_id.split('-capitulo-')
            base_url = f'https://img.lermanga.org/{chapter_id[0].upper()}/{chpt_split[0]}/capitulo-{chpt_split[1]}/'
            options = soup.find('div', {'class': 'nvs slc'}).find_all('option', {'selected': False})
            for option in options:
                pages.append(
                    base_url + option['value'] + '.jpg'
                )
            img_test = get(pages[0])
            if img_test.status_code != 200:
                return [base_url + str(option['value']).zfill(2) + '.png'  for option in options]
                # I don't found a way to discover the image extension, 
                # so I'm just trying to change it to png when jpg don't response.
            return pages
        return False
    