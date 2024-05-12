from backend.interfaces import AnimeDl
from backend.models import Chapter, Episode, Manga
from bs4 import BeautifulSoup
from requests import Session


class AnimesOnlineNZDl(AnimeDl):
    def __init__(self):
        self.base_url = 'https://animesonline.nz'
        self.session = Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Alt-Used': 'animesonline.nz',
            'Connection': 'keep-alive',
            'Referer': 'https://animesonline.nz/',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
        })

    def search(self, query: str) -> list[Manga] | bool:
        response = self.session.get(
            self.base_url,
            params={'s': query},
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            div_results = soup.find_all('div', {'class': 'result-item'})
            animes = []
            for div in div_results:
                a = div.find_all('a')[1]
                img = div.find('img')
                animes.append(
                    Manga(
                        id=a['href'].split('/')[-2],
                        name=a.text,
                        folder_name=a['href'].split('/')[-2],
                        cover=img['src'],
                    )
                )
            return animes[:10]
        return False

    def get_episodes(self, anime_id: str) -> list[Chapter] | bool:
        response = self.session.get(f'{self.base_url}/animes/{anime_id}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            ul = soup.find('ul', {'class': 'episodios'})
            episodes = []
            for li in ul.find_all('li'):
                a = li.find('a')
                split_url = a['href'].split('/')
                episodes.append(
                    Chapter(
                        id=split_url[-2],
                        number=a.text,
                        title=a['title']
                    )
                )
            return episodes[::-1]
        return False

    def get_episode_url(self, episode_id: str) -> Episode | list[Episode] | str:
        response = self.session.get(f'{self.base_url}/episodio/{episode_id}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            iframes = soup.find_all('iframe')
            labels = soup.find_all('span', {'class': 'title'})
            if len(iframes) == 1:
                return Episode(
                    url=iframes[0]['src'],
                    label=labels[0].text
                )
            if len(iframes) > 1:
                return [
                    Episode(
                        url='https://animesonline.nz/noa/?id=ZnA0MGNjMDA0bWI3',
                        label=label.text
                    )
                    for iframe, label in zip(iframes, labels)
                ]
        return f'{self.base_url}/episodio/{episode_id}'
