import flet as ft
from screen.user_control.app_bar import NavBar
from screen.router_manager import Router


__version__ = '0.7b'


def __main__(page: ft.Page):
    page.title = f'MangaYouKnow {__version__}'
    page.theme_mode = 'dark'
    page.appbar = NavBar(page)
    myRouter = Router(page)
    page.on_route_change = myRouter.route_change
    page.update()


ft.app(target=__main__)
    