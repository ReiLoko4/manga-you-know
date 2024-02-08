from backend.interfaces import AnimeDl
from backend.models import Chapter, Manga, Episode
from requests import Session
from bs4 import BeautifulSoup


class OtakuAnimessDl(AnimeDl):
    def __init__(self):
        self.base_url = 'https://otakuanimess.cc'
        self.session = Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Alt-Used': 'otakuanimess.cc',
            'Connection': 'keep-alive',
            'Referer': 'https://otakuanimess.cc/',
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
            div_results = soup.find_all('div', {'class': 'ultAnisContainerItem'})
            animes = []
            for div in div_results:
                a = div.find('a')
                split_url = a['href'].split('/')
                animes.append(
                    Manga(
                        id=split_url[-2],
                        name=div.find('div', {'class': 'aniNome'})
                        .text.replace('\n', '').replace('\r', '').strip(),
                        folder_name=split_url[-2],
                        cover=div.find('img')['src']
                    )
                )
            return animes[:10]
        return False

    def get_episodes(self, anime_id: str) -> list[Chapter] | bool:
        response = self.session.get(f'{self.base_url}/animes/{anime_id}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            episodes_a = soup.find_all('a', {'class': 'list-epi'})
            episodes = []
            for a in episodes_a:
                episodes.append(
                    Chapter(
                        id=a['href'].split('/')[-4],
                        number=a.text.split(' ')[-1] if not 'Filme' in a.text else a.text,
                    )
                )
            return episodes[::-1]
        return False

    def get_episode_url(self, episode_id: str) -> Episode | list[Episode] | bool:
        response = self.session.get(f'{self.base_url}/episodio/{episode_id}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            videos = soup.find_all('video')
            headers = {
                'Referer': 'https://otakuanimess.cc/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
                'Accept': 'video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5',
                'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'video',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site',
            }
            if len(videos) == 1:
                return Episode(
                    url=videos[0].find('source')['src'],
                    label=soup.find('div', {'aba-target': '1'}).text,
                    headers=headers
                )
            return [
                Episode(
                    url=video.find('source')['src'],
                    label=soup.find('div', {'aba-target': f'{i}'}).text,
                    headers=headers
                )
                for i, video in enumerate(videos)
            ]
        return False