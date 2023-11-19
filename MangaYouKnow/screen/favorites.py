import flet as ft
import flet_core.margin as margin
import flet_core.padding as padding
from backend.models import Chapter
from backend.database import DataBase
from backend.manager import Downloader


class Favorites:
    def __init__(self, page: ft.Page):
        dl = Downloader()
        source_languages = {
            'md_id': [
                'en', 'pt-br', 
                'es', 'ja-ro',
                'ko-ro', 'zh',
                'es-la', 'zh-hk',
                'zh-ro'
            ],
            'ml_id': ['pt-br'],
            'ms_id': ['en'],
            'mc_id': ['pt-br'], 
            'mf_id': ['en'],
            'mx_id': ['pt-br'],
            'gkk_id': ['pt-br'],
            'tsct_id': ['pt-br'],
            'tcb_id': ['en'],
            'op_id': ['en'],
            'opex': ['pt-br']
        }
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
            images_b64 = dl.get_base64_images(pages)
            page.data['chapter_images'] = images_b64
            page.data['manga_chapters'] = chapters
            page.data['manga_id'] = manga[source] if source != 'opex' else source
            page.data['chapter_id'] = chapter_id
            page.data['source'] = source
            page.go('/reader')


        def open_manga(info: dict):
            btn_is_readed_list = []
            def togle_readed(source, manga, chapter_id):
                if database.is_readed(source, manga[source] if source != 'opex' else source, chapter_id):
                    database.delete_readed(source, manga[source] if source != 'opex' else source, chapter_id)
                else:
                    database.add_readed(source, manga[source] if source != 'opex' else source, chapter_id)
                each_readed = database.is_each_readed(source, manga[source] if source != 'opex' else source, chapters_by_source[f'{source}_{language_options.value}'])
                icon = ft.icons.REMOVE
                for i, btn in enumerate(btn_is_readed_list):
                    if each_readed[i]:
                        icon = ft.icons.CHECK
                    btn.icon = icon
                page.update()
            chapter_search = ft.TextField(
                label='Capítulo...',
                width=240,
                border_radius=20,
                height=40,
                border_color=ft.colors.GREY_700,
                focused_border_color=ft.colors.BLUE_300
            )
            list_chapters = ft.Column(height=8000, width=240, scroll='always')
            sources = [i for i in list(info.keys()) if i.endswith('_id') and info[i] != None]
            options = []
            is_op = False
            for source in sources:
                match source:
                    case 'md_id':
                        text = 'MangaDex'
                    case 'ml_id':
                        text = 'MangaLivre'
                    case 'ms_id':
                        text = 'MangaSee'
                    case 'mc_id':
                        text = 'MangasChan'
                    case 'mf_id':
                        text = 'MangaFire'
                    case 'mx_id':
                        text = 'MangaNexus'
                    case 'gkk_id':
                        text = 'Gekkou Scans'
                    case 'tsct_id':
                        text = 'Taosect Scans'
                    case 'tcb_id':
                        text = 'TCB Scans'
                    case 'op_id':
                        text = 'OP Scans'
                options.append(ft.dropdown.Option(source, text))
                if info[source] in [
                    '5/one-piece',
                    'One-Piece',
                    13,
                    '13',
                    'dkw',
                    'a1c7c817-4e59-43b7-9365-09675a149a6f',
                ] and not is_op:
                    is_op = True
                    options.append(ft.dropdown.Option('opex', 'One Piece Ex'))
            chapters_by_source = {}
            source_options = ft.Dropdown(
                options=options,
                width=140,
                value=sources[0]
            )
            language_options = ft.Dropdown(
                options=[ft.dropdown.Option(i, i) for i in source_languages[source_options.value]],
                width=140,
                value=source_languages[source_options.value][0]
            )
            if len(sources) == 1:
                source_options.disabled = True
            if len(source_languages[source_options.value]) == 1:
                language_options.disabled = True
                
            def load_chapters(query: str=None):
                btn_is_readed_list.clear()
                language_options.options = [ft.dropdown.Option(i, i) for i in source_languages[source_options.value]]
                if len(source_languages[source_options.value]) == 1:
                    language_options.value = source_languages[source_options.value][0]
                    language_options.disabled = True
                source_options.disabled = True
                language_options.disabled = True
                download_all.disabled = True
                list_chapters.controls = [
                    ft.Row(
                        [
                            ft.ProgressRing(height=120, width=120)
                        ], alignment=ft.MainAxisAlignment.CENTER, width=230
                    )
                ]
                page.update()
                if chapters_by_source.get(f'{source_options.value}_{language_options.value}'):
                    chapters: list[Chapter] = chapters_by_source[f'{source_options.value}_{language_options.value}']
                else:
                    chapters = dl.get_chapters(source_options.value, info.get(source_options.value) if source_options.value != 'opex' else None) if len(source_languages[source_options.value]) == 1 \
                        else dl.get_chapters(source_options.value, info[source_options.value], language_options.value) 
                    chapters_by_source[f'{source_options.value}_{language_options.value}'] = chapters
                list_chapters.controls = []
                is_each_readed = database.is_each_readed(
                    source_options.value, 
                    info.get(source_options.value) 
                    if source_options.value != 'opex' else source, 
                    chapters
                )
                icon = ft.icons.REMOVE
                if not chapters:
                    list_chapters.controls = [
                        ft.ListTile(
                            title=ft.Text(
                                'Nenhum capítulo encontrado nesse idioma, jovem!' if query == None else f'Nenhum resultado para "{query}"'
                            ),
                        )
                    ]
                    if len(source_languages[source_options.value]) > 1:
                        language_options.disabled = False
                    if len(sources) > 1:
                        source_options.disabled = False
                    page.update()
                    return
                for i, chapter in enumerate(chapters):
                    if is_each_readed[i]:
                        icon = ft.icons.CHECK
                    btn_read = ft.IconButton(icon, on_click=lambda e, source=source_options.value, manga=info, chapter_id=chapter.id: togle_readed(source, manga, chapter_id))
                    btn_is_readed_list.append(btn_read)
                    if query and chapter.number:
                        if str(query).lower() not in str(chapter.number).lower():
                            continue
                    list_chapters.controls.append(
                        ft.ListTile(
                            title=ft.Text(chapter.number if chapter.number else chapter.title, tooltip=chapter.title),
                            trailing=btn_read,
                            leading= ft.IconButton(ft.icons.DOWNLOAD_OUTLINED, on_click=lambda e, source=source_options.value, chapter=chapter: dl.download_chapter(info, source, chapter)),
                            on_click=lambda e, source=source_options.value, chapter_id=chapter.id: read(source, info, chapter_id, chapters),
                            key=chapter.number if chapter.number else chapter.title
                        )
                    )
                if len(source_options.options) > 1:
                    source_options.disabled = False
                if len(source_languages[source_options.value]) > 1:
                    language_options.disabled = False
                download_all.disabled = False
                page.update()
            download_all = ft.ElevatedButton(
                text='Baixar tudo',
                on_click=lambda e: dl.download_all_chapters(info, source_options.value, chapters_by_source[f'{source_options.value}_{language_options.value}']))
            source_options.on_change = lambda e: load_chapters()
            language_options.on_change = lambda e: load_chapters()
            chapter_search.on_change = lambda e: load_chapters(e.control.value if e.control.value != '' else None)
            alert = ft.AlertDialog(
                title=ft.Text(info['name'] if len(info['name']) < 40 else f'{info['name'][0:37]}...', tooltip=info['name']),
                content=ft.Container(
                    ft.Row([
                        ft.Column([
                            ft.Container(ft.Image(info['cover'], height=250, fit=ft.ImageFit.FIT_HEIGHT, border_radius=10), padding=5),
                            source_options,
                            language_options,
                            download_all,
                        ]),
                        ft.Column([
                            chapter_search,
                            ft.Card(list_chapters, width=250, height=420)
                        ])
                    ]), height=500, width=430
                )
            )
            page.dialog = alert
            alert.open = True
            page.update()
            load_chapters()

        def edit_manga(info: dict):
            change_name = ft.TextField(label='Nome', value=info['name'])
            change_cover = ft.TextField(label='Capa', value=info['cover'])
            def save(column, content):
                if database.set_manga(info['id'], column, content):
                    row_mangas.controls = load_mangas()
                    page.update()
            edition = ft.AlertDialog(
                title=ft.Text('Editar Mangá'),
                content=ft.Container(
                    ft.Column([
                        change_name,
                        change_cover,
                    ])
                ),
            )
            change_name.on_change = lambda e: save('name', e.control.value)
            change_cover.on_change = lambda e: save('cover', e.control.value)
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
                            ft.Container(ft.Text(i['name'] if len(i['name']) < 25 else f'{i['name'][0:20]}...', tooltip=i['name']),
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
            row_mangas.controls = load_mangas(query=search.value if search.value != '' else None)
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

        self.content = ft.Row(
                [
                    stack
                ],
                scroll='always',
            )

        self.content.data = [update, resize]

    def return_content(self) -> ft.Row:
        return self.content
