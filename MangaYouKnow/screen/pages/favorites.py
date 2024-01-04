import flet as ft
from backend.models import Chapter
from backend.database import DataBase
from backend.managers import DownloadManager
from screen.constants import Language
from screen.components import MangasCard


class Favorites:
    def __init__(self, page: ft.Page) -> None:
        dl: DownloadManager = page.data['dl']
        source_languages = Language.LANGUAGE
        database = DataBase()
        search = ft.TextField(
            label='Pesquisar Favoritos...',
            width=500,
            border_radius=20,
            border_color=ft.colors.GREY_700,
            focused_border_color=ft.colors.BLUE_300
        )
        def reset_field_value(e):
            if not search.value:
                return
            search.value = ''
            row_mangas.controls = load_mangas()
            page.update()	
        reset_search = ft.IconButton(
            ft.icons.HIGHLIGHT_REMOVE_OUTLINED,
            on_click=reset_field_value
        )
        mark_selector = ft.Dropdown(
            options=[
                ft.dropdown.Option('all', 'Todos'),
            ],
            width=140,
            value='all'
        )
        mark_selector.options.extend([ft.dropdown.Option(i['id'], i['name'][:14]) for i in database.get_marks()])
        mark_add = ft.IconButton(
            ft.icons.ADD_ROUNDED,
            icon_color=ft.colors.WHITE,
            bgcolor=ft.colors.BLUE_400,
        )
        def mark_add_click(_=None):
            column_marks = ft.Column(
                scroll='always',
            )
            def load_marks():
                saved_marks = database.get_marks()
                mark_selector.options = [
                    ft.dropdown.Option('all', 'Todos'),
                ]
                mark_selector.options.extend([ft.dropdown.Option(i['id'], i['name'][:14]) for i in saved_marks])
                column_marks.controls = [
                    ft.ListTile(
                        title=ft.TextField(
                                value=i['name'],
                                on_blur=lambda e, mark_id=i['id']: edit_mark(mark_id, e.control.value),
                                on_submit=lambda e, mark_id=i['id']: edit_mark(mark_id, e.control.value)
                            ),
                        trailing=ft.IconButton(
                            ft.icons.HIGHLIGHT_REMOVE,
                            on_click=lambda e, mark_id=i['id']: delete_mark(mark_id)
                        )
                    )
                    for i in saved_marks
                ] if saved_marks else [ft.Text('Nenhuma marcação salva', bgcolor=ft.colors.GREY_700)]
                if len(saved_marks) > 5:
                    column_marks.height = 400
                page.update()
            name_field = ft.TextField(label='Nome')
            def save(_=None):
                if not name_field.value:
                    return
                if database.add_mark(name_field.value):
                    name_field.value = ''
                    load_marks()
            name_field.on_submit = save
            def edit_mark(mark_id: int, name: str):
                if not name:
                    return
                if database.edit_mark(mark_id, name):
                    load_marks()

            def delete_mark(mark_id: int):
                if not database.delete_mark(mark_id):
                    return
                if mark_selector.value == str(mark_id):
                    mark_selector.value = 'all'
                    row_mangas.controls = load_mangas(search.value if search.value != '' else None)
                    page.update()
                load_marks()
            saved_marks = database.get_marks()
            load_marks()
            if len(saved_marks) > 5:
                column_marks.height = 400
            alert = ft.AlertDialog(
                title=ft.Text('Editar marcações'),
                content=ft.Container(
                    ft.Column([
                        name_field,
                        ft.ElevatedButton('Criar marcação', on_click=save),
                        ft.Card(
                            column_marks,
                        )
                    ])
                )
            )
            page.dialog = alert
            alert.open = True
            page.update()
        mark_add.on_click = mark_add_click
        def read(source, manga, chapter: Chapter, chapters: list[dict], language: str=None) -> None:
            page.dialog.content = ft.Container(
                ft.Column([
                    ft.ProgressRing(height=120, width=120),
                ])
            )
            page.update()
            pages = dl.get_chapter_image_urls(source, chapter.id)
            images_b64 = dl.get_base64_images(pages)
            page.data['chapter_images'] = images_b64
            page.data['manga_chapters'] = chapters
            page.data['chapter_title'] = f'{chapter.title} - {chapter.number}' if chapter.title else chapter.number
            page.data['manga_name'] = manga['name']
            page.data['manga_id'] = manga['id']
            page.data['manga_source_id'] = manga[source] if source != 'opex' else source
            page.data['chapter_id'] = chapter.id
            page.data['source'] = source
            if language:
                page.data['language'] = language
            page.go('/reader')

        def remove_manga(manga_id):
            def delete(_=None):
                if database.delete_favorite(int(manga_id)):
                    row_mangas.controls = load_mangas()
                    confirmation.open = False
                    page.update()

            def cancel(_=None):
                confirmation.open = False
                page.update()

            confirmation = ft.AlertDialog(
                title=ft.Row([ft.Text('Tem certeza?')], alignment=ft.MainAxisAlignment.CENTER),
                actions=[ft.Row([
                    ft.IconButton(ft.icons.CHECK_CIRCLE_OUTLINED, tooltip='Confirmar', on_click=delete),
                    ft.IconButton(ft.icons.CANCEL_OUTLINED, tooltip='Cancelar', on_click=cancel)
                ],
                    width=210, alignment=ft.MainAxisAlignment.SPACE_AROUND
                )

                ],
            )
            page.dialog = confirmation
            confirmation.open = True
            page.update()

        row_mangas = ft.Row(
            wrap=True,
            width=page.width - 90,
            top=100,
            alignment=ft.MainAxisAlignment.START
        )
        def load_mangas_by_mark():
            row_mangas.controls = load_mangas(search.value if search.value else None)
            page.update()
        def load_mangas(query: str = None) -> list[ft.Card]:
            return MangasCard(
                source_languages,
                row_mangas,
                mark_selector,
                search,
                load_mangas_by_mark,
                load_mangas,
                read,
                remove_manga,
                page,
                query=query
            )
        # page.data['load_mangas'] = load_mangas
        row_mangas.controls = load_mangas()
        mark_selector.on_change = lambda e: load_mangas_by_mark()
        favorites = database.get_favorites()
        stack = ft.Stack([
            ft.Row([
                ft.Container(search, padding=10),
                reset_search,
                ft.Container(ft.Row([mark_selector, mark_add]), width=250, padding=10),
            ], alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.Divider(height=170, color='white'),
            row_mangas
        ],
            width=page.width - 90,
            height=len(favorites) * 360
        )

        def update(e=None):
            if e:
                row_mangas.width = e
                stack.width = e
            favorites = database.get_favorites()
            count = 0
            for num in range(len(favorites)):
                if num % 3 == 0:
                    count += 1
            stack.height = count * 435
            if page.data['last_favorites'] == favorites:
                return
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
