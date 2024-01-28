import webbrowser
import flet as ft
from backend.database import DataBase
import pyperclip

class About:
    def __init__(self, page: ft.Page):
        database = DataBase()
        
        def open_twitter(_=None):
            webbrowser.open('https://discord.gg/uCC78vQXrE', autoraise=False)
        
        def copy(_=None):
            pyperclip.copy('ec49a9dc-93ab-4e54-ab97-4234c13ce1f8')

        self.content = ft.Row(
            [
                ft.Card(width=400, height=800, content=ft.Column([
                    ft.Text('Opa! Obrigado por usar MangaYouKnow! S2. \nAbaixo você pode acessar o servidor Discord do projeto\nQualquer coisa que quiser falar ou quiser se manter atualizado, de uma olhada!'),
                    ft.Text('Assim que possível responderei tudo. Feedbacks são apreciados.'),
                    ft.Row([
                        ft.Text('Discord MangaYouKnow'),
                        ft.IconButton(ft.icons.OPEN_IN_BROWSER_ROUNDED, on_click=open_twitter, tooltip='Abrir no navegador')
                    ]),
                    ft.Text('Se quiser contribuir com o projeto em forma de doação, abaixo está meu pix. \nToda ajuda é bem vinda!'),
                    ft.Row([
                        ft.TextField(value='ec49a9dc-93ab-4e54-ab97-4234c13ce1f8', read_only=True, height=40, border_radius=10, width=340),
                        ft.IconButton(ft.icons.CONTENT_COPY_ROUNDED, on_click=copy, tooltip='Copiar')

                    ])
            ], alignment=ft.CrossAxisAlignment.CENTER, height=800))
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            width=1000
        )

    def return_content(self):
        return self.content
