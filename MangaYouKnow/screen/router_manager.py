import flet as ft
from screen.index import Index
from screen.favorites import Favorites
from screen.configs import Configs



class Router:
    def __init__(self, page:ft.Page):
        self.page = page
        self.ft = ft
        self.routes = {
            '/': Index(page),
            '/favorites': Favorites(page),
            '/configs': Configs(page)
        }
        self.body = ft.Container(content=self.routes['/'])

    def route_change(self, route:ft.RouteChangeEvent):
        self.body.content = self.routes[route.route]
        self.body.update()

