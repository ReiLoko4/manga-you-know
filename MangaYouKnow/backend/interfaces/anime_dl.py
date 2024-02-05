from abc import ABC, abstractmethod


class AnimeDl(ABC):
    @abstractmethod
    def search(self, query: str, *args):
        pass
    
    @abstractmethod
    def get_episodes(self, anime_id: str | int, *args):
        pass

    @abstractmethod
    def get_episode_url(self, episode_id: str | int, *args):
        pass
