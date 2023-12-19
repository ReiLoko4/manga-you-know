import flet as ft
import flet_core.margin as margin
import flet_core.padding as padding
from backend.database import DataBase
from screen.components import MangaOpen, MangaEdit


database = DataBase()

def togle_notify(e: ft.ControlEvent, manga: dict) -> None:
    if e.control.value:
        database.add_notify(manga['id'])
        return
    database.delete_notify(manga['id'])

def MangasCard(
        source_languages: dict,
        row_mangas: ft.Row,
        mark_selector: ft.Dropdown,
        search: ft.TextField,
        load_mangas_by_mark: callable,
        read: callable,
        remove_manga: callable,
        page: ft.Page,
        query: str = None,
    ) -> list[ft.Card]:
    favorites = database.get_database(None if mark_selector.value == 'all' else mark_selector.value)
    if mark_selector.value == 'all':
        page.data['last_favorites'] = favorites
    if query is not None:
        favorites = [i for i in favorites if query.lower() in i['name'].lower()]
        if not len(favorites):
            return [
                ft.Card(
                    content=ft.Text(
                        f'Não existe nenhum manga que contenha "{query}" nos seus favoritos' if mark_selector.value == 'all'
                        else f'Não existe nenhum manga que contenha "{query}" nos seus favoritos com a marcação "{database.get_mark(mark_selector.value)['name']}"'
                    )
                )
            ]
    if not len(favorites) and mark_selector.value == 'all':
        return [
            ft.Card(
                content=ft.Text('Nada adicionado por enquanto...')
            )
        ]
    if mark_selector.value != 'all' \
        and not len(favorites):
        return [
            ft.Card(
                content=ft.Text(f'Não existe nenhum manga com a marcação "{database.get_mark(mark_selector.value)['name']}" nos seus favoritos')
            )
        ]
    return [
        ft.Card(
            ft.Row([
                ft.Column([
                    ft.Container(
                        ft.Row([
                            ft.Text(i['name'] if len(i['name']) < 24 else f'{i['name'][0:20]}...', tooltip=i['name'])
                        ], alignment=ft.MainAxisAlignment.CENTER, width=170),
                        margin=margin.only(left=5, top=5)
                    ),
                    ft.Row([ft.Image(i['cover'], height=250, fit=ft.ImageFit.FIT_HEIGHT, border_radius=10)],
                            width=180, alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(
                        ft.Row([
                            ft.IconButton(ft.icons.MENU_BOOK, on_click=lambda e, info=i: MangaOpen(info, source_languages, read, togle_notify, page)),
                            ft.IconButton(ft.icons.EDIT_SQUARE, on_click=lambda e, info=i: MangaEdit(info, row_mangas, load_mangas_by_mark, MangasCard, search, page)),
                            ft.IconButton(ft.icons.HIGHLIGHT_REMOVE, on_click=lambda e, info=i: remove_manga(info['id']))
                        ], alignment=ft.MainAxisAlignment.CENTER, width=180), padding=padding.only(top=-5))
                ], alignment=ft.CrossAxisAlignment.STRETCH)
            ], alignment=ft.MainAxisAlignment.CENTER)
            ,
            height=340,
            width=190,
        )
        for i in favorites
    ]
