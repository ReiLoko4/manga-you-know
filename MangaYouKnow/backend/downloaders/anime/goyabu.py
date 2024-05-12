from backend.interfaces import AnimeDl
from backend.models import Chapter, Episode, Manga
from bs4 import BeautifulSoup
from requests import Session


class GoyabuDl(AnimeDl):
    def __init__(self):
        self.base_url = 'https://goyabu.to'
        self.session = Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://goyabu.to/',
            'Alt-Used': 'goyabu.to',
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
            params={
                's': query
            }
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            div_results = soup.find('div', {'class': 'postContent'})
            article_results = div_results.find_all('article', {'class': 'boxAN'})
            animes = []
            for article in article_results:
                a = article.find('a')
                split_url = a['href'].split('/')
                animes.append(
                    Manga(
                        id=split_url[-1],
                        name=article.find('div', {'class': 'title'}).text,
                        folder_name=split_url[-1],
                        cover=article.find('img')['src']
                    )
                )
            return animes[:10]
        return False
    
    def get_episodes(self, anime_id: str) -> list[Chapter] | bool:
        response = self.session.get(f'{self.base_url}/anime/{anime_id}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            ul_results = soup.find('ul', {'class': 'listaEps'})
            episodes_a = ul_results.find_all('a')
            episodes = []
            for a in episodes_a:
                episodes.append(
                    Chapter(
                        id=a['href'].split('/')[-1],
                        number=a['id'].split(' ')[-1] if 'ep' in a['id'] else a['id']
                    )
                )
            return episodes
        return False
    
    def get_episode_url(self, episode_id: str) -> Episode | bool:
        response = self.session.get(f'{self.base_url}/{episode_id}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            url = soup.find('iframe')['src']
            return Episode(
                url=url
            )
        return f'{self.base_url}/{episode_id}'