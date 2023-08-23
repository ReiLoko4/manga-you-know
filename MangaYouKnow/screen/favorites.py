import flet as ft
from backend.database import DataBase
from backend.downloader.mangalivre import MangaLivreDl


class Favorites:
    def __init__(self, page: ft.Page):
        dl = MangaLivreDl()
        database = DataBase()
        search = ft.TextField(
            label='Pesquisar Favoritos...', 
            width=500, 
            border_radius=20, 
            border_color=ft.colors.GREY_700,
            focused_border_color= ft.colors.BLUE_300
        )
        def read(id_release, id_chapter, info:dict, chapters:list[dict]):
            print(f'capitulooo {id_release}')
            page.data['id'] = info['id']
            page.data['name'] = info['name']
            page.data['folder_name'] = info['folder_name']
            page.data['manga_chapters'] = chapters
            page.data['id_chapter'] = id_chapter
            page.data['chapter_images'] = dl.get_manga_chapter_imgs(id_release)
            page.go('/reader')
        def open(info):
            alert = ft.AlertDialog(
                title=ft.Text(info['name']), 
                content=ft.Container(ft.ProgressRing(), height=200)             
            )
            page.dialog = alert
            alert.open = True
            page.update()
            # chapters = database.get_data_chapters(info['folder_name'])
            # if not chapters:
            chapters = dl.get_manga_chapters(info['id'], True)
            page.dialog.content = ft.Column([
                ft.Card(
                    ft.Row([
                        ft.Text(i['number']),
                        ft.IconButton(
                            ft.icons.BOOK, 
                            on_click=lambda e, id_release=i['releases'][list(i['releases'].keys())[0]]['id_release'], id_chapter=i['id_chapter']: read(id_release, id_chapter, info, chapters)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_EVENLY))
                for i in chapters
            ], 
            height=3000,
            scroll='always'
            )
            page.update()

        def remove_manga(manga_id):
            if database.delete_manga(manga_id):
                row_mangas.controls = load_mangas()
                page.update()

        def load_mangas() -> list[ft.Card]:
            favorites = database.get_database()
            return [
                ft.Card(
                    ft.Row([
                        ft.Column([
                        ft.Text(i['name']),
                        ft.Image(i['cover'], height=250, fit=ft.ImageFit.FIT_HEIGHT, border_radius=10),
                        ft.Row([
                            ft.IconButton(ft.icons.MENU_BOOK, on_click=lambda e, info=i:open(info)),
                            ft.IconButton(ft.icons.HIGHLIGHT_REMOVE, on_click=lambda e, info=i:remove_manga(info['id']))
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ], alignment=ft.CrossAxisAlignment.STRETCH)
                    ], alignment=ft.MainAxisAlignment.CENTER)
                    ,
                    height=340,
                    width=190,
                )
                for i in favorites
            ]
        
        row_mangas = ft.Row(
            load_mangas(),
            wrap=True,
            width=page.width - 90,
            top=100,
            alignment=ft.MainAxisAlignment.START
        )
        # def resize(e:ft.ControlEvent):
        #     row_mangas.width = float(e.control.width) - 100
        #     row_mangas.update()
        #     stack.width = float(e.control.width) - 100
        #     stack.update()
        # page.on_resize = resize
        favorites = database.get_database()
        stack = ft.Stack([
            ft.Row([ft.Container(search, padding=10)], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=170, color='white'),
            row_mangas
        ],
            width=page.width - 90,
            height= len(favorites) * 360
        )
        def update(e):
            row_mangas.width = e
            stack.width = e
            favorites = database.get_database()
            stack.height = len(favorites) * 360
            row_mangas.controls = load_mangas()
            page.update()

        def resize(e):
            row_mangas.width = float(e.control.width) - 90
            stack.width = float(e.control.width) - 90
            page.update()

        self.content = ft.Row(
            [  
                stack
            ],
        )

        self.content.data = [update, resize]

    def return_content(self) -> ft.Row:
        return self.content

