import flet as ft
from backend.database import DataBase
from backend.tables import Favorite


database = DataBase()
def MangaEdit(
            manga_info: Favorite, row_mangas: ft.Row, 
            load_mangas_by_mark: callable, load_mangas: callable,
            search: ft.TextField, page: ft.Page
        ) -> ft.AlertDialog:
    change_name = ft.TextField(label='Nome', value=manga_info.name)
    change_cover = ft.TextField(label='Capa', value=manga_info.cover)
    marks = database.get_marks()
    def change_mark(mark_id: int, value: bool):
        if value:
            database.add_mark_favorite(manga_info.id, mark_id)
            load_mangas_by_mark()
            return
        database.delete_mark_favorite(manga_info.id, mark_id)
        load_mangas_by_mark()
    marks_column = ft.Column([
        ft.ListTile(
            title=ft.Text(
                i.name,
            ),
            trailing=ft.Checkbox(
                value=database.is_marked(manga_info.id, i.id),
                on_change=lambda e, mark_id=i.id: change_mark(mark_id, e.control.value)
            )
        )
        for i in marks
    ], scroll='always')
    if len(marks) > 7:
        marks_column.height = 400
    def save(column, content):
        if content == getattr(manga_info, column):
            return
        if database.set_favorite(manga_info.id, column, content):
            row_mangas.controls = load_mangas(search.value if search.value != '' else None)
            page.update()
    edition = ft.AlertDialog(
        title=ft.Text('Editar Mangá'),
        content=ft.Container(
            ft.Column([
                change_name,
                change_cover,
                ft.Card(
                    marks_column,
                )
            ])
        ),
    )
    change_name.on_submit = lambda e: save('name', e.control.value)
    change_name.on_blur = lambda e: save('name', e.control.value)
    change_cover.on_submit = lambda e: save('cover', e.control.value)
    change_cover.on_blur = lambda e: save('cover', e.control.value)
    page.dialog = edition
    edition.open = True
    page.update()
