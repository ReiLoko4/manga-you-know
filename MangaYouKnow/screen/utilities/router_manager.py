import flet as ft
from screen.pages import *


class Router:
    def __init__(self, page: ft.Page):
        self.page = page
        index = Index(page).return_content()
        about = About(page).return_content()
        configs = Configs(page).return_content()
        favorites = Favorites(page).return_content()
        self.routes = {
            '/': index,
            '/favorites': favorites,
            '/configs': configs,
            '/about': about,
        }
        self.body = ft.Container(
            content=self.routes['/'],
            col=11,
        )
        self.espacer = ft.Container(
            bgcolor=ft.colors.TRANSPARENT,
            col=1,
        )
        self.update = {
            '/': index.data[0],
            '/favorites': favorites.data[0],
            '/configs': configs
        }
        self.resize = {
            '/': index.data[1],
            '/favorites': favorites.data[1],
            '/configs': configs
        }

    def route_change(self, r: ft.RouteChangeEvent):
        self.page.scroll_to(0)
        if r.route == '/reader':
            self.page.data['is_first'] = True
            self.espacer.col = 0
            self.body.col = 12
            for overlay in self.page.overlay:
                if type(overlay) == ft.AlertDialog:
                    overlay.open = False
                if type(overlay) == ft.NavigationRail:
                    overlay.visible = False
            self.page.scroll = False
            reader = MangaReader(self.page).return_content()
            self.body.content = reader
            self.page.on_resized = reader.data['resize']
            return
        for overlay in self.page.overlay:
            if type(overlay) == ft.NavigationRail:
                overlay.visible = True
        self.espacer.col = 1
        self.body.col = 11
        self.body.content = self.routes[r.route]
        self.body.update()
        if r.route == '/favorites' or r.route == '/':
            self.update[r.route](self.page.width - 80)
            self.page.on_resized = self.resize[r.route]
