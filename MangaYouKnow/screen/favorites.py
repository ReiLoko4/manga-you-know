import flet as ft
import flet_core.margin as margin
import flet_core.padding as padding
import requests
import base64
from threading import Thread
from backend.database import DataBase
from backend.manager import Downloader, ThreadManager


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

        def read(source, manga, chapter_id, chapters: list[dict]):
            page.dialog.content = ft.Container(
                ft.Column([
                    ft.ProgressRing(height=120, width=120),
                ])
            )
            page.update()
            pages = dl.get_chapter_image_urls(source, chapter_id)
            images_b64 = []
            def get_base_64_image(url, index: int):
                response = requests.get(url)
                images_b64.append([base64.b64encode(response.content).decode('utf-8'), index])
            threads = ThreadManager()
            for i, image in enumerate(pages):
                threads.add_thread(
                    Thread(
                        target=get_base_64_image,
                        args=(image, i)
                    )
                )
            threads.start()
            threads.join()
            images_b64.sort(key=lambda e: e[1])
            final_images = []
            for image in images_b64:
                final_images.append(image[0])
            page.data['chapter_images'] = final_images
            page.data['manga_chapters'] = chapters
            page.data['chapter_id'] = chapter_id
            page.data['source'] = source
            page.go('/reader')

        def open_manga(info):
            list_chapters = ft.Column(height=8000, width=240, scroll='always')
            sources = [i for i in list(info.keys()) if i.endswith('_id') and info[i] != None]
            options = []
            for source in sources:
                match source:
                    case 'md_id':
                        text = 'MangaDex'
                    case 'ml_id':
                        text = 'MangaLivre'
                    case 'ms_id':
                        text = 'MangaSee'
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
                download_all.disabled = True
                list_chapters.controls = [ft.Row([ft.ProgressRing(height=120, width=120)], alignment=ft.MainAxisAlignment.CENTER, width=230)]
                page.update()
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
                            title=ft.Text(chapter['number'] if chapter['number'] else chapter['title']),
                            trailing=ft.IconButton(icon, disabled=True),
                            on_click=lambda e, source=source_options.value, chapter_id=chapter['id']: read(source, info, chapter_id, chapters)
                        )
                    )
                source_options.disabled = False
                download_all.disabled = False
                page.update()
            download_all = ft.IconButton(
                ft.icons.DOWNLOAD,
                tooltip='Baixar todos capítulos',
                on_click=lambda e: dl.download_all_chapters(info, source_options.value, chapters_by_source[source_options.value]))
            source_options.on_change = load_chapters
            alert = ft.AlertDialog(
                title=ft.Text(info['name'] if len(info['name']) < 40 else f'{info["name"][0:37]}...', tooltip=info['name']),
                content=ft.Container(
                    ft.Row([
                        ft.Column([
                            ft.Container(ft.Image(info['cover'], height=250, fit=ft.ImageFit.FIT_HEIGHT, border_radius=10), padding=5),
                            source_options,
                            download_all
                        ]),
                        ft.Card(list_chapters, width=250)
                    ]), height=500, width=430
                )
            )
            page.dialog = alert
            alert.open = True
            page.update()
            load_chapters()

        def edit_manga(info: dict):
            change_name = ft.TextField(label='Nome', value=info['name'])
            def save(column, content):
                # if database.set_manga(into['id']), key, content):
                if database.set_manga(info['id'], column, content):
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
