import flet as ft
from time import sleep
from backend.downloader import MangaLivreDl
from backend.database import DataBase


def Index(page: ft.Page):
    database = DataBase()   
    results = ft.Column(width=500, spacing=0.7)
    card = ft.Card(ft.Container(results), color='gray', visible=False)
    search = ft.TextField(
        label='Pesquisar Mangás...', 
        width=500,
        border_radius=20,
        border_color=ft.colors.GREY_700,
        focused_border_color= ft.colors.BLUE_300
    )
    downloader = MangaLivreDl()
    index = ft.Stack(width=1300, height=1000)
    manga = ft.Row(visible=False)
    def back_index(e):
        manga.visible = False
        index.visible = True
        page.update()
    
    def manga_page(info_manga):
        index.visible = False
        manga.controls.clear()
        def favorite_manga(e):
            database.add_manga({
                'id':info_manga['id_serie'],
                'name':info_manga['name'],
                'folder_name': info_manga['link'].split('/')[-2]
            })

        container_img = ft.Container(padding=20, bgcolor=ft.colors.GREY_900)
        manga.controls.append(ft.Container(
            ft.Column([
                ft.Row([
                    ft.Container(
                    ft.Row([
                        ft.Container(
                            ft.IconButton(ft.icons.ARROW_BACK_IOS_ROUNDED, on_click=back_index, width=50, height=50),
                            padding=5,
                        ),
                        ft.Container(
                            ft.Text(info_manga['name'], size=23),
                            padding=10,
                            width=1200,
                            height=60
                        )
                    ], alignment=ft.CrossAxisAlignment.CENTER
                    ), bgcolor=ft.colors.GREY_900)
                ]),
                ft.Row([
                    container_img,
                    ft.TextButton('Favoritar mangá', on_click=favorite_manga)
        ])])))
        manga.visible = True
        page.update()
        container_img.content = ft.Image(src=info_manga['cover'], height=400, width=ft.ImageFit.FIT_HEIGHT)
        page.update()

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
                    key='noresult',
                    title=ft.Text('Nenhum mangá encontrado!'),
                    disabled=True,
                    height=40
                )
            )
        else:
            for manga in response:
                results.controls.append(
                    ft.ListTile(
                        key='manga',
                        title=ft.Text(manga['name']),
                        height=45 if len(manga['name']) < 60 else 55,
                        on_click=lambda e, info=manga: manga_page(info)
                    )
                )
            if len(search.value) == 0:
                results.controls.clear()
                card.visible = False
            page.update()
    def out_search(e):
        sleep(0.1)
        card.visible = False
        page.update()
    def focus_search(e):
        if len(results.controls) != 0:
            if results.controls[0].key == 'manga':
                card.visible = True
                page.update()
    search.on_change = search_mangas
    search.on_blur = out_search
    search.on_focus = focus_search

    index.controls.append(
        ft.ResponsiveRow([
            ft.Column([ft.Container(bgcolor='white',width=300)],  col=3),
            ft.Column([search], col=6),
            ft.Column([ft.Container(bgcolor='white', width=300)],col=3),
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND, columns=12
        )
    )
    index.controls.append(
        ft.Row([ft.Text('filler', color='black')], top=100)
    )
    index.controls.append(
        ft.Row([card], top=65, left=245)
    )
    
    content = ft.Row(
        [   
            ft.Stack([
                index,
                manga
            ], width=1000, height=1000)
        ],
    )

    return content
