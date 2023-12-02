import webbrowser
import flet as ft
from backend.database import DataBase
import pyperclip

class About:
    def __init__(self, page: ft.Page):
        database = DataBase()
        
        def open_twitter(_=None):
            webbrowser.open('https://twitter.com/ReiLokoFn', autoraise=False)
        
        def copy(_=None):
            pyperclip.copy('ec49a9dc-93ab-4e54-ab97-4234c13ce1f8')

        self.content = ft.Row(
            [
                ft.Card(width=400, height=800, content=ft.Column([
                    ft.Text('Opa! Obrigado por usar MangaYouKnow! S2. \nNo momento atual não temos um Discord mas providenciarei :)\n Se desejas me perguntar algo pode clicar no botão abaixo do meu Twitter'),
                    ft.Text('Assim que possível responderei suas duvidas. Feedbacks são apreciados.'),
                    ft.Row([
                        ft.Text('Twitter @ReiLokoFn'),
                        ft.IconButton(ft.icons.OPEN_IN_BROWSER_ROUNDED, on_click=open_twitter, tooltip='Abrir no navegador')
                    ]),
                    ft.Text('Se quiser doar qualquer quantia no meu pix já me animara bastante, mas apenas se quiser!'),
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
