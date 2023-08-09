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
            chapters = database.get_data_chapters(info['folder_name'])
            if not chapters:
                chapters = dl.get_manga_chapters(info['id'], True)
            alert = ft.AlertDialog(
                title=ft.Text(info['name']), 
                content=ft.Column([
                    ft.Card(
                    ft.Row([
                        ft.Text(i['number']),
                        ft.IconButton(
                            ft.icons.READ_MORE_OUTLINED, 
                            on_click=lambda e, id_release=i['releases'][list(i['releases'].keys())[0]]['id_release'], id_chapter=i['id_chapter']: read(id_release, id_chapter, info, chapters)
                        )
                    ]))
                    for i in chapters
                ], 
                height=3000,
                scroll='always'
                )                       
                
            )
            page.dialog = alert
            alert.open = True
            page.update()
        
        def load_mangas() -> list[ft.Card]:
            favorites = database.get_database()
            return [
                ft.Card(ft.Column([
                    ft.Text(i['name']),
                    ft.Image(i['cover'], height=200, fit=ft.ImageFit.FIT_HEIGHT),
                    ft.IconButton(ft.icons.READ_MORE, on_click=lambda e, info=i:open(info))
                ],
                    alignment=ft.CrossAxisAlignment.CENTER
                ),
                    height=350,
                    width=210,
                )
                for i in favorites
            ]
        
        row_mangas = ft.Row(
            load_mangas(),
            wrap=True,
            width=page.width - 90,
            top=100,
            alignment=ft.MainAxisAlignment.CENTER
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

