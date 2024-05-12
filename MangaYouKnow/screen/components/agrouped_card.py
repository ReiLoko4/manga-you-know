import flet as ft
from backend.tables import Favorite

def limit_text(text: str, lenght: int) -> str:
    return text[:lenght - 3] + '...' if len(text) > lenght else text

def AgroupedCard(favorite: Favorite) -> ft.Card:
    return ft.Card(
        ft.Card(
            ft.Row([
                ft.Column([
                    ft.Container(
                        ft.Row([
                            ft.Text(limit_text(favorite.name, 24), tooltip=favorite.name)
                        ], alignment=ft.MainAxisAlignment.CENTER, width=170),
                        margin=ft.margin.only(left=5, top=5)
                    ),
                    ft.Row([
                        ft.Image(favorite.cover, height=250, fit=ft.ImageFit.FIT_HEIGHT, border_radius=10)
                        ], width=180, alignment=ft.MainAxisAlignment.CENTER
                    ),
                ], alignment=ft.CrossAxisAlignment.STRETCH)
            ], alignment=ft.MainAxisAlignment.CENTER),
            height=310,
            width=190,
        ), key=favorite.id
    )
