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

    card = ft.Card()


    content = ft.Row(
        [   
            ft.Stack([
                ft.Row([ft.Container(search, padding=10)], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=170, color='white'),
                ft.Row([card])
            ],
            width=1000,
            height=1000)
        ],
    )

    return content
