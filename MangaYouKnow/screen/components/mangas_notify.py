from time import sleep
import flet as ft
from threading import Thread
import flet_core.margin as margin 
import flet_core.padding as padding
from screen.components import MangaOpen
from screen.constants import Language
from backend.database import DataBase
from backend.managers import DownloadManager
from backend.models import Chapter


database = DataBase()


def verify_chapters(manga: dict, text: ft.Text, card: ft.Card, container: ft.Container, page: ft.Page):
    dl: DownloadManager = page.data['dl']
    last_readed = database.get_last_readed(manga['id'])
    if not last_readed:
        last_readed = {}
        last_readed['source'] = [key for key in manga.keys() if key.endswith('_id') and manga[key]][0]
        last_readed['manga_source_id'] = manga[last_readed['source']]
        last_readed['language'] = 'en' if last_readed['source'] == 'md_id' else None
        last_readed['chapter_id'] = None
    chapters: list[Chapter] = dl.get_chapters(last_readed['source'], last_readed['manga_source_id'], last_readed['language'] if last_readed['language'] else None)
    if not last_readed.get('chapter_id'):
        text.value = f'+{len(chapters)}'
        card.key = len(chapters)
        container.border = ft.border.all(1, ft.colors.RED_500)
        page.update()
        return
    count = 0
    for chapter in chapters:
        if chapter.id == last_readed['chapter_id']:
            break
        count += 1
    if count == 0:
        text.value = f'Em dia!'
        container.border = ft.border.all(1, ft.colors.GREEN_500)
        page.update()
        return
    container.border = ft.border.all(1, ft.colors.BLUE_500 if count < 30 else ft.colors.YELLOW_500)
    text.value = f'+{count}'
    card.key = count
    page.update()

def MangasCardNotify(
        cards_row: ft.Row,
        page: ft.Page,
    ) -> list[ft.Card]:
    def togle_notify(e: ft.ControlEvent, manga: dict) -> None:
        database.add_notify(manga['id']) if e.control.value \
            else database.delete_notify(manga['id'])
        cards_row.controls = MangasCardNotify(cards_row, page)
        page.update()
    favorites_notify = database.get_database_notify_on()
    mangas_card = []
    for manga in favorites_notify:
        text_chapters = ft.Text('...', italic=True)
        card = ft.Card(height=340, width=190, key=0)
        container = ft.Container(padding=padding.only(top=-5), border=ft.border.all(1, ft.colors.WHITE), border_radius=5)
        container.content = ft.Row([
            text_chapters,
            ft.IconButton(
                ft.icons.MENU_BOOK, on_click=lambda e, 
                info=manga: MangaOpen(info, Language.LANGUAGE, togle_notify, page, True, cards_row, MangasCardNotify)
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND, width=180)
        card.content = ft.Row([
            ft.Column([
                ft.Container(ft.Text(manga['name'] if len(manga['name']) < 25 else f'{manga['name'][0:20]}...', tooltip=manga['name']), margin=margin.only(left=5, top=5)),
                ft.Row(
                    [ft.Image(manga['cover'], height=250, fit=ft.ImageFit.FIT_HEIGHT, border_radius=10)],
                    width=180, alignment=ft.MainAxisAlignment.CENTER
                ),
                container
            ], alignment=ft.CrossAxisAlignment.STRETCH)
        ], alignment=ft.MainAxisAlignment.CENTER)
        Thread(target=verify_chapters, args=(manga, text_chapters, card, container, page)).start()
        mangas_card.append(card)
    return mangas_card    
