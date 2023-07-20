import flet as ft
from screen.index import Index
from screen.favorites import Favorites
from screen.configs import Configs



class Router:
    def __init__(self, page:ft.Page):
        self.page = page
        self.ft = ft
        index = Index(page)
        favorites = Favorites(page)
        configs = Configs(page)
        self.routes = {
            '/': index,
            '/favorites': favorites,
            '/configs': configs
        }
        self.body = ft.Container(content=self.routes['/'])
        self.update = {
            '/': index,
            '/favorites': favorites.data,
            '/configs': configs
        }
        self.update = {
           '/': index,
           '/favorites': favorites.data[0],
           '/configs': configs
        }
        self.resize = {
            '/': index,
            '/favorites': favorites.data[1],
            '/configs': configs
        }

    def route_change(self, route:ft.RouteChangeEvent):
        self.body.content = self.routes[route.route]
        self.body.update()
        if route.route == '/favorites':
           self.update[route.route](self.page.width-90)
           self.page.on_resize = self.resize[route.route]

