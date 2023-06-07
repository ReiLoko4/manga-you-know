import flet as ft
from pathlib import Path
from threading import Thread
from myk_db import MangaYouKnowDB
from myk_dl import MangaLivreDl, MangaDexDl, GekkouDl, OpexDl


__version__ = '0.7b'


class MangaYouKnowGUI:
    def __init__(self) -> ft.Page:
        self.connection_data = MangaYouKnowDB()
        self.connection_ML = MangaLivreDl()
        self.connection_MD = MangaDexDl()
        self.connection_Gk = GekkouDl()
        self.connection_Op = OpexDl()
        ft.app(self.create_page)

    def create_page(self, page: ft.Page):
        page.title = f'MangaYouKnow {__version__}'
        page.theme_mode = 'dark'
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        btn_back = ft.IconButton(
            ft.icons.ARROW_BACK_IOS
        )
        page.add(
            ft.Row(
                [
                    btn_back,
                    ft.Image(
                        src='mangas/one-punch-man/cover/one-punch-man.jpg',
                        height=page.height,
                        fit=ft.ImageFit.FIT_HEIGHT
                    ),
                    ft.IconButton(ft.icons.ARROW_FORWARD_IOS),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )


MangaYouKnowGUI()