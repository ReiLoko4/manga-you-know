import flet as ft
from backend.downloader import MangaLivreDl


def Index(page: ft.Page):


    results = ft.Column(width=500, spacing=0.2)
    card = ft.Card(ft.Container(results), color='gray', visible=False)
    search = ft.TextField(label='Pesquisar mangás...', width=500, border_radius=20)
    downloader = MangaLivreDl()

    def do_something(info_manga):
        print(info_manga)

    def search_mangas(e:ft.ControlEvent):
        if len(e.control.value) == 0: 
            results.controls.clear()
            card.visible = False
            page.update()
            return False
        response = downloader.search_mangas(e.control.value)
        card.visible = True
        results.controls.clear()
        if e.control.value != search.value:
                return False
        if not response:
            results.controls.append(
                ft.ListTile(
                    title=ft.Text('Nenhum mangá encontrado!'),
                    disabled=True,
                    height=40
                )
            )
        else:
            for manga in response:
                results.controls.append(
                    ft.ListTile(
                        title=ft.Text(manga['name']),
                        height=45 if len(manga['name']) < 60 else 55,
                        on_click=lambda e, info=manga: do_something(info)
                    )
                )
            if len(search.value) == 0:
                results.controls.clear()
                card.visible = False
            page.update()
        
    search.on_change = search_mangas

    content = ft.Row(
        [   
            ft.Stack([
                ft.Row([ft.Container(search, padding=10)]),
                # all content in the row bellow 
                ft.Row([ft.Text('filler', color='black')], top=100),
                ft.Row([card], top=65, left=10)
            ], width=1000, height=1000)
        ],
    )

    return content
