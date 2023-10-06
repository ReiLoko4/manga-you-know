from time import sleep

import flet as ft

from backend.database import DataBase
from backend.manager import Downloader


class Index:
    def __init__(self, page: ft.Page):

        connection_data = DataBase()
        downloader = Downloader()
        source_selector = ft.Dropdown(options=[
            ft.dropdown.Option('md', text='MangaDex'),
            ft.dropdown.Option('ml', text='MangaLivre'),
            ft.dropdown.Option('ms', text='MangaSee'),
            ft.dropdown.Option('mf', text='MangaFire'),
            ft.dropdown.Option('gkk', text='Gekkou'),
            ft.dropdown.Option('tsct', text='Taosect'),
            ft.dropdown.Option('tcb', text='TCB'),
            ft.dropdown.Option('op', text='OP Scans', disabled=True),
        ], value='md', width=120)

        local_search = [
            'ms'
        ]

        results = ft.Column(width=470, spacing=0.7, data={'last_src': '', 'chapters': [] })
        card = ft.Card(ft.Container(results), color='gray', visible=False)
        search = ft.TextField(
            label='Pesquisar Mangás...',
            width=500,
            border_radius=20,
            border_color=ft.colors.GREY_700,
            focused_border_color=ft.colors.BLUE_300,
        )

        index = ft.Stack(width=1300, height=1000)
        manga = ft.Row(visible=False)
        self.is_clicked = False

        def togle_favorite(manga: dict, button: ft.IconButton, is_on_search: bool = False):
            if connection_data.is_favorite(f'{source_selector.value}_id', manga['id']):
                if connection_data.delete_manga_by_key(f'{source_selector.value}_id', manga['id']):
                    button.icon = ft.icons.BOOKMARK_OUTLINE
            else:
                if connection_data.add_manga(
                    manga['name'],
                    manga['folder_name'],
                    manga['cover'],
                    md_id=manga['id'] if source_selector.value == 'md' else None,
                    ml_id=manga['id'] if source_selector.value == 'ml' else None,
                    ms_id=manga['id'] if source_selector.value == 'ms' else None,
                    mf_id=manga['id'] if source_selector.value == 'mf' else None,
                    gkk_id=manga['id'] if source_selector.value == 'gkk' else None,
                    tsct_id=manga['id'] if source_selector.value == 'tsct' else None,
                    tcb_id=manga['id'] if source_selector.value == 'tcb' else None,
                    op_id=manga['id'] if source_selector.value == 'op' else None,
                ):
                    button.icon = ft.icons.BOOKMARK_ROUNDED
            page.update()
            if is_on_search:
                self.is_clicked = True
                sleep(1)
                self.is_clicked = False
                search.focus()
                page.update()

        def manga_page(info_manga):
            button_favorite = ft.IconButton(
                ft.icons.BOOKMARK_ROUNDED if connection_data.is_favorite(f'{source_selector.value}_id', info_manga['id']) else ft.icons.BOOKMARK_OUTLINE,
                height=30)
            button_favorite.on_click = lambda e, info=info_manga, button=button_favorite: togle_favorite(info, button)
            manga_dialog = ft.AlertDialog(
                title=ft.Text(info_manga['name'][0:30], tooltip=info_manga['name']),
                content=ft.Row([
                    ft.Image(src=info_manga['cover'], height=400, width=ft.ImageFit.FIT_HEIGHT, animate_size=300,
                             border_radius=ft.border_radius.all(30)),
                ]),
                actions=[button_favorite]
            )
            manga_dialog.open = True
            page.dialog = manga_dialog

        def search_mangas(e: ft.ControlEvent = None):
            query = e
            if not type(e) == str:
                query = e.control.value
            if len(query) == 0:
                results.controls.clear()
                card.visible = False
                page.update()
                return False
            results.controls.clear()
            results.controls.append(
                ft.ListTile(
                    key='noresult',
                    title=ft.Row([ft.Text('Procurando...'), ft.ProgressRing()],
                                 alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    disabled=True,
                    height=55
                )
            )
            card.visible = True
            page.update()
            response = downloader.search(source_selector.value, query, results.data['chapters'] if results.data['last_src'] == source_selector.value else None)
            if query != search.value:
                    return False
            if source_selector.value in local_search:
                results.data['chapters'] = response[1]
                response = response[0]
                results.data['last_src'] = source_selector.value
            favorites = connection_data.get_database()
            list_favorites_id = [i[f'{source_selector.value}_id'] for i in favorites]
            card.visible = True
            results.controls.clear()
            
            if not response:
                results.controls.append(
                    ft.ListTile(
                        key='noresult',
                        title=ft.Text('Nenhum mangá encontrado!'),
                        disabled=True,
                        height=55
                    )
                )
            else:
                for manga in response:
                    button_favorite = ft.IconButton(ft.icons.BOOKMARK_ROUNDED if manga['id'] in list_favorites_id else ft.icons.BOOKMARK_OUTLINE, height=30)
                    button_favorite.on_click = lambda e, manga=manga, button=button_favorite: togle_favorite(manga, button, True)
                    results.controls.append(
                        ft.ListTile(
                            key='manga',
                            title=ft.Text(f"{manga['name'][0:42]}..." if len(manga['name']) > 45 else manga['name'][0:50], tooltip=manga['name']),
                            height=45,
                            trailing=button_favorite,
                            on_click=lambda e, info=manga: manga_page(info)
                        )
                    )
                if len(search.value) == 0:
                    results.controls.clear()
                    card.visible = False
            page.update()

        def out_search(e):
            sleep(0.1)
            if self.is_clicked:
                return
            card.visible = False
            page.update()

        def focus_search(e):
            if len(results.controls) != 0:
                if results.controls[0].key == 'manga':
                    card.visible = True
                    page.update()
        def togle_visible(_:ft.ControlEvent=None):
            page.update()
            if search.value:
                search.focus()
                search_mangas(search.value)
        source_selector.on_change = togle_visible

        search.on_change = search_mangas
        search.on_blur = out_search
        search.on_focus = focus_search
        index.controls.append(
            ft.ResponsiveRow([
                ft.Column([ft.Container(bgcolor='white', width=300)], col=2),
                ft.Column([ft.Container(search, padding=10)], col=6),
                ft.Column([ft.Container(ft.Row([source_selector]), width=250, padding=10)], col=4),
            ], alignment=ft.MainAxisAlignment.CENTER, columns=12
            )
        )
        index.controls.append(
            ft.Row([], top=100)
        )
        index.controls.append(
            ft.Row([card], top=70, left=175)
        )

        self.content = ft.Column(
            [
                ft.Stack([
                    index,
                    manga
                ], width=1000, height=1000)
            ],
        )

    def return_content(self) -> ft.Row:
        return self.content
