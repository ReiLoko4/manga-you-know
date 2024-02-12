import re

from backend.interfaces import AnimeDl
from backend.models import Chapter, Episode, Manga
from bs4 import BeautifulSoup
from requests import Session


class AnimesVisionDl(AnimeDl):
    def __init__(self):
        self.base_url = 'https://animes.vision'
        self.session = Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://animes.vision/search?nome=coisas',
            'Alt-Used': 'animes.vision',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
        })

    def search(self, query: str):
        response = self.session.get(
            f'{self.base_url}/search',
            params={'nome': query},
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            div_results = soup.find('div', {'class': 'film_list-wrap'})
            animes = []
            for div in div_results.find_all('div', {'class': 'flw-item'}):
                a = div.find('a')
                animes.append(
                    Manga(
                        id=a['href'].split('/')[-1],
                        name=a['title'],
                        folder_name=a['href'].split('/')[-1],
                        cover=div.find('img')['data-src'],
                    )
                )
            return animes[:10]
        return False
    
    def get_episodes_by_content(self, content: str, is_first: bool = False) -> list[Chapter] | bool:
        soup = BeautifulSoup(content, 'html.parser')
        if is_first:
            class_items = 'screen-items'
            items_type = 'div'
            items_class = 'item'
            key_number = 'data-title'
        else:
            class_items = 'ss-list'
            items_type = 'a'
            items_class = 'ssl-item ep-item'
            key_number = 'title'
        div_items = soup.find('div', {'class': class_items})
        chapters = []
        for div in div_items.find_all(items_type, {'class': items_class}):
            if is_first:
                a = div.find('a')
            else:
                a = div
            number = re.search(r'\d+', div[key_number])
            if 'Especial' in div[key_number] and number:
                number = f'Especial {number.group()}'
            else:
                number = number.group() if number else div[key_number]
            chapters.append(
                Chapter(
                    id='/'.join(a['href'].split('/')[-3:]) ,
                    number=number,
                )
            )
        return chapters
    
    def get_page_episodes(self, url: str) -> list[Chapter] | bool:
        response = self.session.get(url)
        if response.status_code == 200:
            return self.get_episodes_by_content(response.content)
        return False

    def get_episodes(self, anime_id: str) -> list[Chapter] | bool:
        response = self.session.get(f'{self.base_url}/animes/{anime_id}')
        if response.status_code == 200:
            episodes = self.get_episodes_by_content(response.content, True)
            soup = BeautifulSoup(response.content, 'html.parser')
            page_links = soup.find_all('a', {'class': 'page-link'})
            if page_links:
                episodes_page = self.get_page_episodes(
                    f'{self.base_url}/animes/{episodes[0].id}'
                )
                episodes_page.insert(0, episodes[0])
                return episodes_page[::-1]
            return episodes[::-1]
        return False

    def get_episode_url(self, episode_id: str) -> Episode | bool:
        response = self.session.get(f'{self.base_url}/animes/{episode_id}')
        if response.status_code == 200:
            file_urls = re.findall(r'"file":\s*"([^"]+)"', response.text)
            labels = re.findall(r'"label":\s*"([^"]+)"', response.text)
            if len(file_urls) == 1:
                return Episode(
                    url=file_urls[0].replace('\\', ''), 
                    label=labels[0],
                    headers={'Referer': 'https://animes.vision/'}
                )
            return [
                Episode(
                    url=url.replace('\\', ''),
                    label=label,
                    headers={'Referer': 'https://animes.vision/'}
                )
                for url, label in zip(file_urls, labels)
            ][::-1]
        return False
            