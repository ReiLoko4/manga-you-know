from backend.interfaces import AnimeDl
from backend.models import Chapter, Episode, Manga
from bs4 import BeautifulSoup
from requests import Session


class AnimesOnlineDl(AnimeDl):
    def __init__(self):
        self.base_url = 'https://animesonlinecc.to'
        self.session = Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Alt-Used': 'animesonlinecc.to',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
        })

    def search(self, query: str) -> list[Manga] | bool:
        response = self.session.get(f'{self.base_url}/search/{query.lower().replace(' ', '+')}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            div_results = soup.find_all('div', {'id': 'archive-content'})
            animes = []
            for div in div_results:
                a = div.find('a')
                href_split = a['href'].split('/')
                img = div.find('img')
                animes.append(
                    Manga(
                        id=href_split[-2],
                        name=img['alt'],
                        folder_name=href_split[-2],
                        cover=img['src'],
                    )
                )
            return animes[:10]
        return False

    def get_episodes(self, anime_id: str) -> list[Chapter] | bool:
        response = self.session.get(f'{self.base_url}/anime/{anime_id}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            ul = soup.find('ul', {'class': 'episodios'})
            episodes = []
            for li in ul.find_all('li'):
                a = li.find_all('a')[-1]
                split_url = a['href'].split('/')
                episodes.append(
                    Chapter(
                        id=split_url[-2],
                        number=a.text.split(' ')[-1]
                    )
                )
            return episodes[::-1]
        return False

    def get_episode_url(self, episode_id: str) -> Episode | list[Episode] | bool:
        response = self.session.get(f'{self.base_url}/episodio/{episode_id}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            div = soup.find('div', {'class': 'content'})
            iframes = div.find_all('iframe')
            a = div.find_all('a', {'class': 'options'})
            if len(iframes) == 1:
                return Episode(
                    url=iframes[0]['src'],
                    label=a[0].text
                )
            return [
                Episode(
                    url=iframe['src'],
                    label=a.text
                ) 
                for iframe, a in zip(iframes, a)
            ]
        return False
