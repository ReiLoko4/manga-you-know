import flet as ft
from screen.user_control.app_bar import NavBar
from screen.utilities.router_manager import Router
from backend.managers import DownloadManager
from backend.database import DataBase


__version__ = '0.9.17b'


database = DataBase()

def main(page: ft.Page) -> ft.FletApp:
    page.title = f'MangaYouKnow {__version__}'
    page.theme_mode = database.get_config()['theme-mode']
    page.window.width = 1200
    page.window.height = 800
    page.window.min_width = 1200
    page.window.min_height = 800
    page.window.center()
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    page.vertical_alignment = ft.CrossAxisAlignment.CENTER
    database.init_database()
    page.data = {}
    page.data['is_first'] = True
    page.data['dl'] = DownloadManager()
    router = Router(page)
    page.on_route_change = router.route_change
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.overlay.append(
        NavBar(page)
    )
    page.add(
        ft.ResponsiveRow([
            router.espacer,
            router.body,
        ])
    )
    page.data['version'] = __version__
    page.go('/')
    page.update()
    