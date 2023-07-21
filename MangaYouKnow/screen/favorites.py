import flet as ft
from backend.database import DataBase


class Favorites:
    def __init__(self, page: ft.Page) :
        database = DataBase()
        search = ft.TextField(
            label='Pesquisar Favoritos...', 
            width=500, 
            border_radius=20, 
            border_color=ft.colors.GREY_700,
            focused_border_color= ft.colors.BLUE_300
        ) 
        favorites = database.get_database()
        row_mangas = ft.Row([
            ft.Card(ft.Column([
                ft.Text(i['name']),
                ft.IconButton(ft.icons.READ_MORE)
            ],
                alignment=ft.CrossAxisAlignment.CENTER
            ),
                height=350,
                width=210,
            )
            for i in favorites
        ],
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
        
        stack = ft.Stack([
            ft.Row([ft.Container(search, padding=10)], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=170, color='white'),
            row_mangas
        ],
            width=page.width - 90,
            height=2000
        )
        def update(e):
            row_mangas.width = e
            stack.width = e
            favorites = database.get_database()
            row_mangas.controls = [
                ft.Card(ft.Column([
                    ft.Text(i['name']),
                    ft.IconButton(ft.icons.READ_MORE)
                ],
                    alignment=ft.CrossAxisAlignment.CENTER
                ),
                    height=350,
                    width=210,
                )
                for i in favorites
            ]
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

