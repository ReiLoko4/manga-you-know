import flet as ft
from backend.database import DataBase

def Favorites(page: ft.Page):
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
        scroll=ft.ScrollMode.ALWAYS
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
        height=1500
    )
    content = ft.Row(
        [   
            stack
        ],
    )

    return content
