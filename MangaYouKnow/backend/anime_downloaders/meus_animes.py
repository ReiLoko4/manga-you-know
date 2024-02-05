from backend.interfaces import AnimeDl
from backend.managers import ThreadManager
from backend.models import Chapter, Manga
from bs4 import BeautifulSoup
from requests import Session


class MeusAnimes(AnimeDl):
    def __init__(self):
        self.base_url = 'https://meusanimes.biz'
        self.session = Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://meusanimes.biz/',
            'Alt-Used': 'meusanimes.biz',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
        })
    
    def search(self, query: str) -> list[Manga] | bool:
        response = self.session.get(
            self.base_url,
            params={'s': query}
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            div_results = soup.find_all('div', {'class': 'aniItem'})
            animes = []
            for div in div_results:
                a = div.find('a')
                href_split = a['href'].split('/')
                animes.append(
                    Manga(
                        id=href_split[-2],
                        name=a['title'],
                        folder_name=href_split[-2],
                        cover=div.find('img')['data-src']
                    )
                )
            return animes[:10]
        return False
    
    def get_episodes_by_url(self, url: str) -> list[Chapter] | bool:
        response = self.session.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            div_results = soup.find('div', {'class': 'animeVideosItem'})
            episodes = []
            for div in div_results:
                a = div.find('a')
                episodes.append(
                    Chapter(
                        id=a['href'].split('/')[-2],
                        number=div.find('img')['alt'].split(' ')[-1]
                    )
                )
            return episodes
        return False

    def get_episodes(self, anime_id: str) -> list[Chapter] | bool:
        response = self.session.get(f'{self.base_url}/anime/{anime_id}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            div_results = soup.find('div', {'class': 'animeVideosItem'})
            episodes = []
            for div in div_results:
                a = div.find('a')
                episodes.append(
                    Chapter(
                        id=a['href'].split('/')[-2],
                        number=div.find('img')['alt'].split(' ')[-1]
                    )
                )
            if len(episodes) == 20:
                page_numbers = soup.find_all('a', {'class': 'page-numbers'})
                if page_numbers:
                    threads = ThreadManager()
                    for index in range(
                        2, int(page_numbers[-1]['href'].text), 1):
                        threads.add_thread_by_args(
                                target=self.get_episodes_by_url,
                                args=(f'{response.url}/page/{index}',)
                        )
                    threads.start()
                    episodes.extend(threads.join())
            episodes.reverse()
            return episodes
        return False

    def get_episode_url(self, episode_id: str) -> str | bool:
        response = self.session.get(f'{self.base_url}/video/{episode_id}')
