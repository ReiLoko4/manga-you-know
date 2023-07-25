import flet as ft
from backend.downloader.mangalivre import MangaLivreDl



class MangaReader:
    def __init__(self, page: ft.Page):
        self.page = page
        self.dl = MangaLivreDl()
        self.pages = self.dl.get_manga_chapter_imgs(page.data['id_chapter'])
        self.images = [ft.Image(i, fit=ft.ImageFit.FIT_WIDTH, height=page.height) for i in self.pages]
        self.content = ft.Container(
            ft.Stack(
                self.images    
            )
        )
