import flet as ft
import flet_core.margin as margin
import flet_core.padding as padding

from MangaYouKnow.backend.database import DataBase
from MangaYouKnow.backend.manager import Downloader


class Favorites:
    def __init__(self, page: ft.Page):
        dl = Downloader()
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
            page.data['chapter_images'] = dl.get_chapter_imgs(id_release)
            page.go('/reader')

        def open_manga(info):
            list_chapters = ft.Column(height=8000, width=240, scroll='always')
            sources = [i for i in list(info.keys()) if i.endswith('_id') and info[i] != None]
            options = []
            for source in sources:
                match source:
                    case 'ml_id':
                        text = 'MangaLivre'
                    case 'md_id':
                        text = 'MangaDex'
                    case 'mf_id':
                        text = 'MangaFire'
                    case 'gkk_id':
                        text = 'Gekkou Scans'
                    case 'tsct_id':
                        text = 'Taosect Scans'
                    case 'tcb_id':
                        text = 'TCB Scans'
                    case 'op_id':
                        text = 'OP Scans'
                options.append(ft.dropdown.Option(source, text))
            chapters_by_source = {}
            source_options = ft.Dropdown(
                options=options,
                width=140,
                value=sources[0]
            )
            def load_chapters(_=None):
                if chapters_by_source.get(source_options.value):
                    list_chapters.controls = chapters_by_source[source_options.value]
                    page.update()
                    return
                source_options.disabled = True
                list_chapters.controls = [ft.Row([ft.ProgressRing(height=120, width=120)], alignment=ft.MainAxisAlignment.CENTER, width=230)]
                page.update()
                print(source_options.value)
                chapters = dl.get_chapters(source_options.value, info[source_options.value])
                chapters_by_source[source_options.value] = chapters
                list_chapters.controls = []
                icon = ft.icons.REMOVE
                for chapter in chapters:
                    # if str(last_readed) == str(chapter['id_chapter']):
                    #     is_readed = True
                    # if is_readed:
                    #     icon = ft.icons.CHECK
                    list_chapters.controls.append(
                        ft.ListTile(
                            title=ft.Text(chapter['number']),
                            trailing=ft.IconButton(icon, disabled=True),
                            on_click=lambda e, :print('fodasse')
                        )
                    )
                source_options.disabled = False
                page.update()

            source_options.on_change = load_chapters
            alert = ft.AlertDialog(
                title=ft.Text(info['name'] if len(info['name']) < 40 else f'{info["name"][0:37]}...', tooltip=info['name']),
                content=ft.Container(
                    ft.Row([
                        ft.Column([
                            ft.Container(ft.Image(info['cover'], height=250, fit=ft.ImageFit.FIT_HEIGHT, border_radius=10), padding=5),
                            source_options
                        ]),
                        ft.Card(list_chapters, width=250)
                    ]), height=500, width=430
                )
            )
            page.dialog = alert
            alert.open = True
            page.update()
            load_chapters()
            # chapters = database.get_data_chapters(info['folder_name'])
            # if not chapters:
            # chapters = dl.get_chapters(info['ml_id'])
            # page.dialog.content = ft.Card(ft.Column(height=3000, scroll='always'))
            # is_readed = False
            # last_readed = info.get('id_last_readed')
            # if last_readed == None:
            #     last_readed = ''
            # icon = ft.icons.REMOVE
            # list_cards = []
            # for chapter in chapters:
            #     if str(last_readed) == str(chapter['id_chapter']):
            #         is_readed = True
            #     if is_readed:
            #         icon = ft.icons.CHECK
            #     list_cards.append(
            #         ft.ListTile(
            #             title=ft.Text(chapter['number']),
            #             trailing=ft.IconButton(icon, disabled=True),
            #             on_click=lambda e, id_release=chapter['releases'][list(chapter['releases'].keys())[0]]['id_release'], id_chapter=chapter['id_chapter']: read(id_release, id_chapter, info, chapters)                    
            #         )
            #     )
            # page.dialog.content.content.controls = list_cards
            # progress_download_all = ft.ProgressBar(value=0.0)
            # page.dialog.actions = [ft.TextButton('Baixar todos capítulos', on_click=lambda e: dl.download_all_manga_chapters(info['ml_id'], chapters, progress_bar=progress_download_all)), progress_download_all]
            # page.update()

        def edit_manga(info: dict):
            change_name = ft.TextField(label='Nome', value=info['name'])
            def save(key, content):
                # if database.set_manga(int(info['id']), key, content):
                if database.execute_data(f'UPDATE favorites SET {key} = "{content}" WHERE id = {int(info["id"])};'):
                    row_mangas.controls = load_mangas()
                    page.update()
            edition = ft.AlertDialog(
                title=ft.Text('Editar Mangá'),
                content=ft.Container(
                    ft.Column([
                        change_name,
                    ])
                ),
            )
            change_name.on_change = lambda e: save('name', e.control.value)
            page.dialog = edition
            edition.open = True
            page.update()

        def remove_manga(manga_id):
            def delete(_=None):
                if database.delete_manga(int(manga_id)):
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
                                    ft.IconButton(ft.icons.MENU_BOOK, on_click=lambda e, info=i: open_manga(info)),
                                    ft.IconButton(ft.icons.EDIT_SQUARE, on_click=lambda e, info=i: edit_manga(info)),
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
