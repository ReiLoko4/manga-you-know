import flet as ft
from backend.database import DataBase
from screen.constants import Language
from screen.components import MangasCard, AgroupedCard


class Favorites:
    def __init__(self, page: ft.Page) -> None:
        source_languages = Language.LANGUAGE
        database = DataBase()
        search = ft.TextField(
            label='Pesquisar Favoritos...',
            width=320,
            border_radius=20,
            border_color=ft.colors.GREY_700,
            focused_border_color=ft.colors.BLUE_300
        )
        count_results = ft.Text(
            '0',
            width=50,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
            color=ft.colors.BLUE_300
        )
        favorite_type = ft.SegmentedButton(
            show_selected_icon=False,
            allow_empty_selection=False,
            allow_multiple_selection=True,
            segments=[
                ft.Segment('manga', label=ft.Text('Manga')),
                ft.Segment('anime', label=ft.Text('Anime')),
            ],
            selected={'manga', 'anime'},
        )
        order_favorites = ft.Dropdown(
            options=[
                ft.dropdown.Option('asc', '+ Velhos'),
                ft.dropdown.Option('desc', '+ Novos'),
                ft.dropdown.Option('more-score', '+ Nota'),
                ft.dropdown.Option('less-score', '- Nota'),
                ft.dropdown.Option('asc-alf', 'A-Z'),
                ft.dropdown.Option('desc-alf', 'Z-A'),
            ],
            width=100,
            value='asc'
        )
        def reset_field_value(e):
            if not search.value:
                return
            search.value = ''
            load_mangas()
            page.update()	
        reset_search = ft.IconButton(
            ft.icons.HIGHLIGHT_REMOVE_OUTLINED,
            on_click=reset_field_value,
        )
        def get_mark_name() -> str:
            for option in mark_selector.options:
                if str(option.key) == str(mark_selector.value):
                    return option.text
        def show_agrouped_favorites(e):
            agrouped_row = ft.Row(
                [ft.ProgressRing(height=200, width=200, color=ft.colors.BLUE_500, key='progress')], 
                wrap=True, height=10000, alignment=ft.MainAxisAlignment.START, scroll='always'
            )
            def close_dialog(_=None):
                dialog.open = False
                page.update()
            dialog = ft.AlertDialog(
                title=ft.Row(
                    [ft.Text(get_mark_name(), size='xl'), ft.IconButton(ft.icons.CLOSE, on_click=close_dialog)],
                    expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                content=agrouped_row
            )
            page.dialog = dialog
            dialog.open = True
            page.update()
            favorites_by_mark = database.get_favorites(mark_selector.value if mark_selector.value != 'all' else None)
            agrouped_row.controls.clear()
            for favorite in favorites_by_mark:
                try:
                    agrouped_row.controls.append(AgroupedCard(favorite))
                except Exception as e:
                    print(e)
            page.update()
        show_agrouped = ft.IconButton(
            ft.icons.BOOKMARKS_ROUNDED,
            on_click=show_agrouped_favorites,
        )
        mark_selector = ft.Dropdown(
            options=[
                ft.dropdown.Option('all', 'Todos'),
            ],
            width=140,
            value='all'
        )
        mark_selector.options.extend([ft.dropdown.Option(mark.id, mark.name[:14]) for mark in database.get_marks()])
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
                mark_selector.options.extend([ft.dropdown.Option(i.id, i.name[:14]) for i in saved_marks])
                column_marks.controls = [
                    ft.ListTile(
                        title=ft.TextField(
                                value=mark.name,
                                on_blur=lambda e, mark_id=mark.id: edit_mark(mark_id, e.control.value),
                                on_submit=lambda e, mark_id=mark.id: edit_mark(mark_id, e.control.value)
                            ),
                        trailing=ft.IconButton(
                            ft.icons.HIGHLIGHT_REMOVE,
                            on_click=lambda e, mark_id=mark.id: delete_mark(mark_id)
                        )
                    )
                    for mark in saved_marks
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
                    load_mangas()
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
       
        def remove_manga(manga_id):
            def delete(_=None):
                if database.delete_favorite(int(manga_id)):
                    load_mangas()
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
        def load_mangas(query: str = None):
            if query == None:
                query = search.value if search.value != '' else None
            if query: query = query.lower()
            favorites = MangasCard(
                source_languages,
                mark_selector,
                load_mangas,
                remove_manga,
                page,
                order_favorites.value,
                query=query,
                favorite_type=list(favorite_type.selected)
            )
            row_mangas.controls = favorites
            if favorites[0].key == 'nothing':
                count_results.value = '0'
                page.update()
                return
            count_results.value = str(len(favorites))
            page.update()
        # page.data['load_mangas'] = load_mangas
        order_favorites.on_change = lambda e: load_mangas()
        favorite_type.on_change = lambda e: load_mangas()  
        load_mangas()
        mark_selector.on_change = lambda e: load_mangas()
        favorites_by_mark = database.get_favorites()
        stack = ft.Stack([
            ft.Row([
                ft.Container(favorite_type, padding=10),
                ft.Container(order_favorites, padding=10),
                ft.Container(search, padding=10),
                reset_search,
                show_agrouped,
                ft.Container(ft.Column([count_results], alignment=ft.MainAxisAlignment.CENTER), height=60, border=ft.border.all(1, ft.colors.GREY_700), border_radius=20, padding=5),
                ft.Container(ft.Row([mark_selector, mark_add]), width=250, padding=10),
            ], alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.Divider(height=170, color='white'),
            row_mangas
        ],
            width=page.width - 90,
            height=len(favorites_by_mark) * 360
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
            load_mangas()
            page.update()

        def search_favorites(e):
            if len(e.control.value) == 0:
                load_mangas()
                page.update()
                return
            load_mangas(e.control.value)
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
