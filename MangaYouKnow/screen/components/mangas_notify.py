from time import sleep
from typing import Generator

import flet as ft
from threading import Thread
import flet_core.margin as margin 
import flet_core.padding as padding
from .error_gif import ErrorGif
from screen.components import MangaOpen
from screen.constants import Language, LOADING_B64_GIF
from backend.database import DataBase
from backend.managers import DownloadManager, ThreadManager
from backend.models import Chapter
from backend.tables import Favorite, Readed
from backend.utilities import Notificator


database = DataBase()
notificator = Notificator()

threads = ThreadManager()
manga_len = {}

def verify_chapters(manga: Favorite, text: ft.Text, card: ft.Card, container: ft.Container, page: ft.Page):
    dl: DownloadManager = page.data['dl']
    last_readed = database.get_last_readed(manga.id)
    if not last_readed:
        last_readed = Readed()
        last_readed.source = manga.source
        last_readed.favorite_source_id = manga.source_id
        last_readed.language = 'en' if last_readed.source == 'md' else None
        last_readed.chapter_id = None
    try:
        if manga.type in ('manga', 'hq'):
            chapters: list[Chapter] = dl.get_chapters(last_readed.source, last_readed.favorite_source_id, last_readed.language if last_readed.language else None)
        else:
            chapters: list[Chapter] = dl.get_episodes(last_readed.source, last_readed.favorite_source_id)
    except:
        text.value = 'Error!!!'
        container.border = ft.border.all(1, ft.colors.RED_500)
        page.update()
        return
    if last_readed.chapter_id is None:
        page.data[manga.id] = f'0/{len(chapters)}'
        text.value = f'+{len(chapters)}'
        card.key = len(chapters)
        container.border = ft.border.all(1, ft.colors.RED_500)
        page.update()
        return
    is_each_readed = database.is_each_readed(last_readed.source, manga.id, last_readed.favorite_source_id, chapters)
    count = 0
    for is_read in is_each_readed:
        if is_read:
            break
        count += 1
    if manga_len.get(manga.id):
        if  len(chapters) > manga_len[manga.id]:
            notificator.show(f'Novos capítulos de {manga.name}!', f'Foram adicionados {len(chapters) - manga_len[manga.id]} capítulos novos')
    manga_len[manga.id] = len(chapters)
    if count == 0:
        page.data[manga.id] = f'{len(chapters)}/{len(chapters)}'
        text.value = f'Em dia!'
        container.border = ft.border.all(1, ft.colors.GREEN_500)
        page.update()
        return
    page.data[manga.id] = f'{count}/{len(chapters)}'
    container.border = ft.border.all(1, ft.colors.BLUE_500 if count < 30 else ft.colors.YELLOW_500)
    text.value = f'+{count}'
    card.key = count
    page.update()
    
def verify_ten_minutes():
    while True:
        try:
            threads.start()
            threads.restart()
        except Exception as e:
            print(e)
        sleep(600)

def MangasCardNotify(
        cards_row: ft.Row,
        page: ft.Page,
    ) -> Generator[ft.Card, None, None]:
    def togle_notify(e: ft.ControlEvent, manga: Favorite) -> None:
        database.add_notify(manga.id) if e.control.value \
            else database.delete_notify(manga.id)
        cards_row.controls.clear()
        for i, favorite_card in enumerate(
            MangasCardNotify(cards_row, page)):
            cards_row.controls.append(favorite_card)
            if i % 3 == 0:
                page.update()
        page.update()
    favorites_notify = database.get_favorites_notify()
    threads.delete_all()
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
                ft.Container(
                    ft.Row([
                        ft.Text(manga.name if len(manga.name) < 24 else f'{manga.name[0:20]}...', tooltip=manga.name)
                    ], alignment=ft.MainAxisAlignment.CENTER, width=170),
                    margin=margin.only(left=5, top=5)
                ),
                ft.Row(
                    [ft.Image(manga.cover, error_content=ErrorGif(), height=250, width=170, fit=ft.ImageFit.FIT_HEIGHT, border_radius=10)],
                    width=180, alignment=ft.MainAxisAlignment.CENTER
                ),
                container
            ], alignment=ft.CrossAxisAlignment.STRETCH)
        ], alignment=ft.MainAxisAlignment.CENTER)
        threads.add_thread_by_args(verify_chapters, args=(manga, text_chapters, card, container, page))
        yield card
    threads.start()
    # if page.data['is_first']:
    #     page.data['is_first'] = False
    #     Thread(target=verify_ten_minutes).start()
    # else:
    #     threads.start()
