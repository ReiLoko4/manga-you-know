import json
import re

from backend.interfaces import AnimeDl
from backend.managers import ThreadManager
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
    
    def get_episodes_by_content(self, content: str) -> list[Chapter] | bool:
        soup = BeautifulSoup(content, 'html.parser')
        div_items = soup.find('div', {'class': 'screen-items'})
        chapters = []
        for div in div_items.find_all('div', {'class': 'item'}):
            a = div.find('a')
            number = re.search(r'\d+', div['data-title'])
            if 'Especial' in div['data-title'] and number:
                number = f'Especial {number.group()}'
            else:
                number = number.group() if number else div['data-title']
            chapters.append(
                Chapter(
                    id='/'.join(a['href'].split('/')[-3:]),
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
            episodes = self.get_episodes_by_content(response.content)
            soup = BeautifulSoup(response.content, 'html.parser')
            page_links = soup.find_all('a', {'class': 'page-link'})
            if page_links:
                threads = ThreadManager()
                for i in range(2, int(page_links[-2].text) + 1, 1):
                    threads.add_thread_by_args(
                        self.get_page_episodes,
                        (f'{self.base_url}/animes/{anime_id}?page={i}',)
                    )
                threads.start()
                for episodes_page in threads.join():
                    episodes.extend(episodes_page)
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
                    label=labels[0]
                )
            return [
                Episode(
                    url=url.replace('\\', ''),
                    label=label
                )
                for url, label in zip(file_urls, labels)
            ][::-1]
        return False
            