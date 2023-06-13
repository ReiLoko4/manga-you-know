import flet as ft
from time import sleep
from pathlib import Path
from threading import Thread
from MangaYouKnow.database import DataBase
from MangaYouKnow.downloader import MangaLivreDl, MangaDexDl, GekkouDl, OpexDl




__version__ = '0.7b'


class MangaYouKnowGUI:
    def __init__(self) -> ft.Page:
        self.connection_data = DataBase()
        self.connection_ML = MangaLivreDl()
        self.connection_MD = MangaDexDl()
        self.connection_Gk = GekkouDl()
        self.connection_Op = OpexDl()
        ft.app(self.create_page)

    def create_page(self, page: ft.Page):
        page.title = f'MangaYouKnow {__version__}'
        page.theme_mode = ft.ThemeMode.DARK
        page.window_min_height = 600
        page.window_min_width = 900
        home = ft.NavigationRailDestination(
            icon=ft.icons.HOME_OUTLINED,
            selected_icon=ft.icons.HOME_ROUNDED,
            label='Home',
        )
        favorites = ft.NavigationRailDestination(
            icon=ft.icons.BOOKMARK_OUTLINE,
            selected_icon=ft.icons.BOOKMARK_ROUNDED,
            label='Favoritos',
        )
        configs = ft.NavigationRailDestination(
            icon=ft.icons.SETTINGS_OUTLINED,
            selected_icon=ft.icons.SETTINGS_ROUNDED,
            label='Configurações',
        )
        rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=400,
            group_alignment=-0.9,
            destinations=[
                home,
                favorites,
                configs
            ]
        )
        search_entry = ft.TextField(label='Pesquisar mangas...', width=510, border_radius=20)
        results = ft.Column(width=500)
        result_search = ft.Card(
            color='gray', 
            visible=False,
            content=ft.Container(
                results
            )
        )
        def manga_view(e):
            home_container.visible = False
            manga_container.visible = True
            manga_page_content.controls.append(ft.Text(f'manga é {e.control.key}'))
            page.update()

        def search_mangas(e:ft.ControlEvent):
            if len(e.control.value) == 0: 
                results.controls.clear()
                result_search.visible = False
                page.update()
                return False
            search = self.connection_ML.search_mangas(e.control.value)
            result_search.visible = True
            if not search:
                results.controls.clear()
                results.controls.append(
                        ft.ListTile(
                            title=ft.Text('Nenhum mangá encontrado!'),
                            disabled=True,
                            height=40
                        )
                    )
                result_search.height = 60
                page.update()
            else:
                results.controls.clear()
                for manga in search:
                    results.controls.append(
                        ft.ListTile(
                            key=manga['name'],
                            title=ft.Text(manga['name']),
                            height=50,
                            on_click=manga_view
                        )
                    )
                result_search.height = len(results.controls) * 61
                page.update()
        
        search_entry.on_change = search_mangas
        search_entry.on_submit = search_mangas
        def out_search(e):
            sleep(0.09)
            result_search.visible = False
            page.update()
        search_entry.on_blur = out_search
        def focus(e):
            if len(results.controls) != 0:
                result_search.visible = True
                page.update()
        search_entry.on_focus = focus

        home_container = ft.Container(
            content=ft.Row([
                ft.Stack(
                    [ft.Column([
                        search_entry
                    ]),
                    ft.Column([
                        result_search,
                    ],
                    left=0,
                    top=40,
                    ),
                    ]
                ),
                ft.Column(
                    [
                        ft.Text('nada')
                    ],
                )
                
                ], 
                alignment=ft.CrossAxisAlignment.START,
            )
        )

        manga_page_content = ft.Row([
            ft.Text('thats the manga container'),
        ])
        manga_container = ft.Container(
            content=manga_page_content,
            visible=False
        )
        favorite_container = ft.Container(
            content=ft.Text("This is Tab 2"),
            visible=False,
        )
        configs_container = ft.Container(
            content=ft.Text("This is Tab 3"),
            visible=False
        )
        stack = ft.Stack(
            [
                ft.Row([home_container]),
                ft.Row([manga_container]),
                ft.Row([favorite_container]),
                ft.Row([configs_container])
            ],
            height=page.height
        )
        def change_tab(e):
            if e.control.selected_index == 0:
                if not home_container.visible:
                    home_container.visible = True
                    favorite_container.visible = False
                    configs_container.visible = False
            elif e.control.selected_index == 1:
                if not favorite_container.visible:
                    home_container.visible = False
                    favorite_container.visible = True
                    configs_container.visible = False
            else:
                if not configs_container.visible:
                    home_container.visible = False
                    favorite_container.visible = False
                    configs_container.visible = True
            page.update()
        rail.on_change = change_tab
        page.add(ft.Row(
                [
                    rail,
                    ft.VerticalDivider(width=1),
                    stack
                ],
                width=1000,
                height=page.height - 20
            )
        )
        page.update()


MangaYouKnowGUI()
