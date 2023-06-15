import flet as ft


def Index(page: ft.Page):
    content = ft.Row(
        [
            ft.Row([ft.TextField(label='Pesquisar mangás...')])
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    return content
