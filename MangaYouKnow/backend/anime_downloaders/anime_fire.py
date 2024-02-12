from backend.interfaces import AnimeDl
from backend.models import Chapter, Episode, Manga
from bs4 import BeautifulSoup
from requests import Session


class AnimeFireDl(AnimeDl):
    def __init__(self):
        self.base_url = 'https://animefire.plus'
        self.session = Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://animefire.plus/',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Connection': 'keep-alive',
        })

    def search(self, query: str) -> list[Manga] | bool:
        response = self.session.get(f'{self.base_url}/pesquisar/{query.lower().replace(' ', '-')}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            div_results = soup.find('div', {'class': 'card-group'})
            animes = []
            for div in div_results.find_all('div', {'class': 'col-6 col-sm-4 col-md-3 col-lg-2 mb-1 minWDanime divCardUltimosEps'}):
                a = div.find('a')
                animes.append(
                    Manga(
                        id=a['href'].split('/')[-1],
                        name=div.find('h3', {'class': 'animeTitle'}).text,
                        folder_name=a['href'].split('/')[-1],
                        cover=div.find('img')['data-src'],
                    )
                )
            return animes[:10]
        return False    

    def get_episodes(self, anime_id: str) -> list[Chapter] | bool:
        response = self.session.get(f'{self.base_url}/animes/{anime_id}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            div_results = soup.find('div', {'class': 'div_video_list'})
            episodes = []
            for a in div_results.find_all('a'):
                split_url = a['href'].split('/')
                episodes.append(
                    Chapter(
                        id=f'{split_url[-2]}/{split_url[-1]}',
                        number=split_url[-1]
                    )
                )
            return episodes[::-1]
        return False

    def get_episode_url(self, episode_id: str) -> Episode | bool:
        response = self.session.get(f'{self.base_url}/animes/{episode_id}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            video = soup.find('video', {'id': 'my-video'})
            if not video:
                return soup.find('iframe')['src']
            video_json = self.session.get(video['data-video-src'])
            if video_json.status_code == 200:
                return [
                    Episode(
                        url=episode['src'],
                        label=episode['label']
                    )
                    for episode in video_json.json()['data']
                ][::-1]
            return False
        return False