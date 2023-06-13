import flet as ft


class Router:
    def __init__(self, page:ft.Page):
        self.page = page
        self.ft = ft
        self.routes = {
            '/': '',
            '/favorites': '',
            '/settings': ''
        }
        self.body = ft.Container(content=self.routes['/'])

    def route_change(self, route:ft.RouteChangeEvent):
        self.body.content = self.routes([route.route])
        self.body.update()
