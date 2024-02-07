from backend.interfaces import AnimeDl
from backend.models import Chapter, Episode, Manga
from bs4 import BeautifulSoup
from requests import Session


class AnimesHouseDl(AnimeDl):
    def __init__(self):
        self.base_url = 'https://animeshouse.net'
        self.session = Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Accept': '*/*',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://animeshouse.net',
            'Alt-Used': 'animeshouse.net',
            'Connection': 'keep-alive',
            'Referer': 'https://animeshouse.net/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
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
                a = div.find('a')
                img = div.find('img')
                split_url = a['href'].split('/')
                animes.append(
                    Manga(
                        id=split_url[-2],
                        name=img['alt'],
                        folder_name=split_url[-2],
                        cover=img['src'],
                    )
                )
            return animes[:10]
        return False
    
    def get_episodes(self, anime_id: str) -> list[Chapter] | bool:
        response = self.session.get(
            f'{self.base_url}/anime/{anime_id}'
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            div_eps = soup.find('div', {'id': 'serie_contenido'})
            episodes = []
            for li in div_eps.find_all('li'):
                a = li.find('a')
                split_url = a['href'].split('/')
                episodes.append(
                    Chapter(
                        id=split_url[-2],
                        number=a.text.split(' ')[-1]
                    )
                )
            return episodes[::-1]
        return False
    
    def get_episode_url(self, episode_id: str) -> Episode | bool:
        response = self.session.get(
            f'{self.base_url}/episodio/{episode_id}'
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            ul = soup.find('ul', {'id': 'playeroptionsul'})
            li_opt = ul.find_all('li')
            span_opt = ul.find_all('span', {'class': 'title'})
            if len(li_opt) == 1:
                data_post = li_opt[0]['data-post']
                response = self.session.post(
                    f'{self.base_url}/wp-admin/admin-ajax.php',
                    data = {
                    'action': 'doo_player_ajax',
                    'post': data_post,
                    'nume': '1',
                    'type': 'tv',
                })
                print(response.content)
                soup = BeautifulSoup(response.content, 'html.parser')
                url = soup.find('iframe')['src']
                return Episode(
                    url=url,
                    label=span_opt[0].text.split(' ')[-1],
                    header={'Referer':f'https://{url.split('/')[2]}'}
                )
            episode_urls = []
            for li, span in zip(li_opt, span_opt):
                data_post = li['data-post']
                response = self.session.post(
                    f'{self.base_url}/wp-admin/admin-ajax.php',
                    data = {
                    'action': 'doo_player_ajax',
                    'post': data_post,
                    'nume': '1',
                    'type': 'tv',
                })
                print(response.content)
                soup = BeautifulSoup(response.content, 'html.parser')
                url = soup.find('iframe')['src']
                episode_urls.append(
                    Episode(
                        url=url,
                        label=span.text.split(' ')[-1],
                        headers={'Referer':f'https://{url.split('/')[2]}'}
                    )
                )
            return episode_urls
        return False
    