import flet as ft

from screen.pages import Index, Favorites, Configs, MangaReader, About


class Router:
    def __init__(self, page: ft.Page):
        self.page = page
        self.ft = ft
        index = Index(page).return_content()
        favorites = Favorites(page).return_content()
        configs = Configs(page).return_content()
        about = About(page).return_content()
        self.routes = {
            '/': index,
            '/favorites': favorites,
            '/configs': configs,
            '/about': about
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
        self.reader = ft.Container()
        self.reader.visible = False

    def route_change(self, route: ft.RouteChangeEvent):
        self.page.scroll_to(0)
        if route.route == '/reader':
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
        self.body.content = self.routes[route.route]
        self.body.update()
        if route.route == '/favorites':
            self.update[route.route](self.page.width - 90)
            self.page.on_resize = self.resize[route.route]
