import flet as ft
from screen.pages import *


class Router:
    def __init__(self, page: ft.Page):
        self.page = page
        self.ft = ft
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
        self.body = ft.Container(content=self.routes['/'])
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
        self.reader = ft.Container()
        self.reader.visible = False

    def route_change(self, r: ft.RouteChangeEvent):
        self.page.scroll_to(0)
        if r.route == '/reader':
            self.page.dialog.open = False
            self.page.scroll = False
            reader = MangaReader(self.page).return_content()
            self.reader.content = reader
            self.page.on_resize = reader.data['resize']
            self.body.visible = False
            self.reader.visible = True
            return
        if self.reader.visible:
            self.reader.visible = False
            self.body.visible = True
            self.page.banner.visible = True
        self.body.content = self.routes[r.route]
        self.body.update()
        if r.route == '/favorites' or r.route == '/':
            self.update[r.route](self.page.width - 80)
            self.page.on_resize = self.resize[r.route]
