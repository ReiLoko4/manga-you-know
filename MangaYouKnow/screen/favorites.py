import flet as ft
import flet_core.margin as margin
import flet_core.padding as padding
from backend.database import DataBase
from backend.downloader.mangalivre import MangaLivreDl

import trio


class Favorites:
    def __init__(self, page: ft.Page):
        dl = MangaLivreDl()
        database = DataBase()
        search = ft.TextField(
            label='Pesquisar Favoritos...',
            width=500,
            border_radius=20,
            border_color=ft.colors.GREY_700,
            focused_border_color=ft.colors.BLUE_300
        )

        def read(id_release, id_chapter, info: dict, chapters: list[dict]):
            print(f'capitulooo {id_release}')
            page.data['id'] = info['id']
            page.data['name'] = info['name']
            page.data['folder_name'] = info['folder_name']
            page.data['manga_chapters'] = chapters
            page.data['id_chapter'] = id_chapter
            page.data['chapter_images'] = trio.run(dl.get_manga_chapter_imgs, id_release)
            page.go('/reader')

        def open(info):
            alert = ft.AlertDialog(
                title=ft.Text(info['name'] if len(info['name']) < 23 else f'{info["name"][0:20]}...',
                              tooltip=info['name']),
                content=ft.Container(ft.ProgressRing(), height=200)
            )
            page.dialog = alert
            alert.open = True
            page.update()
            # chapters = database.get_data_chapters(info['folder_name'])
            # if not chapters:
            chapters = trio.run(dl.get_manga_chapters, info['id'])
            page.dialog.content = ft.Column(height=3000, scroll='always')
            is_readed = False
            last_readed = info.get('id_last_readed')
            if last_readed == None:
                last_readed = ''
            icon = ft.icons.REMOVE
            list_cards = []
            for chapter in chapters:
                if str(last_readed) == str(chapter['id_chapter']):
                    is_readed = True
                if is_readed:
                    icon = ft.icons.CHECK
                list_cards.append(
                    ft.Card(
                        ft.Row([
                            ft.Text(chapter['number']),
                            ft.IconButton(icon, disabled=True),
                            ft.IconButton(
                                ft.icons.BOOK,
                                on_click=lambda e, id_release=chapter['releases'][list(chapter['releases'].keys())[0]][
                                    'id_release'], id_chapter=chapter['id_chapter']: read(id_release, id_chapter, info,
                                                                                          chapters)
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
                    )
                )
            page.dialog.content.controls = list_cards
            page.update()

        def remove_manga(manga_id):
            def delete(_=None):
                if database.delete_manga(manga_id):
                    row_mangas.controls = load_mangas()
                    confirmation.open = False
                    page.update()

            def cancel(_=None):
                confirmation.open = False
                page.update()

            confirmation = ft.AlertDialog(
                title=ft.Text('Tem certeza?'),
                actions=[ft.Row([
                    ft.IconButton(ft.icons.CHECK_CIRCLE_OUTLINED, tooltip='Confirmar', on_click=delete),
                    ft.IconButton(ft.icons.CANCEL_OUTLINED, tooltip='Cancelar', on_click=cancel)
                ],
                    width=180, alignment=ft.MainAxisAlignment.CENTER
                )

                ],
            )
            page.dialog = confirmation
            confirmation.open = True
            page.update()

        def load_mangas(query: str = None) -> list[ft.Card]:
            favorites = database.get_database()

            if query is not None:
                favorites = [i for i in favorites if query.lower() in i['name'].lower()]
                if len(favorites) == 0:
                    return [
                        ft.Card(
                            content=ft.Text(f'Não existe nenhum mangá que contenha "{query}" nos seus favoritos')
                        )
                    ]

            return [
                ft.Card(
                    ft.Row([
                        ft.Column([
                            ft.Container(ft.Text(i['name'] if len(i['name']) < 25 else f'{i["name"][0:20]}...', tooltip=i['name']),
                                         margin=margin.only(left=5, top=5)),
                            ft.Row([ft.Image(i['cover'], height=250, fit=ft.ImageFit.FIT_HEIGHT, border_radius=10)],
                                   width=180, alignment=ft.MainAxisAlignment.CENTER),
                            ft.Container(
                                ft.Row([
                                    ft.IconButton(ft.icons.MENU_BOOK, on_click=lambda e, info=i: open(info)),
                                    ft.IconButton(ft.icons.EDIT_SQUARE, disabled=True, tooltip='Em breve!'),
                                    ft.IconButton(ft.icons.HIGHLIGHT_REMOVE,
                                              on_click=lambda e, info=i: remove_manga(info['id']))
                                ], alignment=ft.MainAxisAlignment.CENTER, width=180), padding=padding.only(top=-5))
                        ], alignment=ft.CrossAxisAlignment.STRETCH)
                    ], alignment=ft.MainAxisAlignment.CENTER)
                    ,
                    height=340,
                    width=190,
                )
                for i in favorites
            ]

        row_mangas = ft.Row(
            load_mangas(),
            wrap=True,
            width=page.width - 90,
            top=100,
            alignment=ft.MainAxisAlignment.START
        )
        # def resize(e:ft.ControlEvent):
        #     row_mangas.width = float(e.control.width) - 100
        #     row_mangas.update()
        #     stack.width = float(e.control.width) - 100
        #     stack.update()
        # page.on_resize = resize
        favorites = database.get_database()
        stack = ft.Stack([
            ft.Row([ft.Container(search, padding=10)], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=170, color='white'),
            row_mangas
        ],
            width=page.width - 90,
            height=len(favorites) * 360
        )

        def update(e=None):
            if not e == None:
                row_mangas.width = e
                stack.width = e
            favorites = database.get_database()

            count = 0
            for num in range(len(favorites)):
                if num % 3 == 0:
                    count += 1

            stack.height = count * 435
            row_mangas.controls = load_mangas()
            page.update()

        def search_favorites(e):
            if len(e.control.value) == 0:
                row_mangas.controls = load_mangas()
                page.update()
                return
            row_mangas.controls = load_mangas(e.control.value)
            page.update()

        search.on_change = search_favorites

        def resize(e):
            row_mangas.width = float(e.control.width) - 90
            stack.width = float(e.control.width) - 90

            page.update()

        self.content = ft.Container(
            ft.Column(
                [
                    stack
                ],
            ),
        )
        self.content.scroll = ft.ScrollMode.ALWAYS
        self.content.data = [update, resize]

    def return_content(self) -> ft.Row:
        return self.content
