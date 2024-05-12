import flet as ft
from backend.database import DataBase
from backend.managers import DownloadManager
from backend.tables import Favorite
from backend.models import Chapter
from backend.utilities import EnableBackwardIterator


class MangaReader:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = DataBase()
        self.dl: DownloadManager = self.page.data['dl']
        self.manga: Favorite = self.page.data['manga']
        self.source = self.page.data['source']
        self.language = self.page.data.get('language')
        self.chapter: Chapter = self.page.data['chapter']
        self.chapters: list[Chapter] = self.page.data['manga_chapters']
        if not self.db.is_readed(self.source, self.manga.id, self.manga.source_id if self.manga.source_id != 'opex' else 'opex', self.chapter.id, self.language):
            self.db.add_all_readed_below(self.manga, self.source, self.chapter, self.chapters, self.language)
        self.chapters_column = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.drawer = ft.NavigationDrawer(
            controls=[
                ft.Card(content=self.chapters_column),
            ],
        )
        is_each_readed = self.db.is_each_readed(
            self.source, 
            self.manga.id,
            self.manga.source_id
            if self.source != 'opex' else 'opex', 
            self.chapters
        )
        self.btns_list: list[ft.IconButton] = []
        icon = ft.icons.REMOVE
        for is_readed, chapter in zip(is_each_readed, self.chapters):
            if is_readed:
                icon = ft.icons.CHECK
            btn_read = ft.IconButton(
                icon, on_click=lambda e, 
                source=self.source, manga=self.manga, chapter=chapter, \
                    language=self.language: \
                        self.togle_readed(source, manga, chapter, language)
            )
            self.btns_list.append(btn_read)
            # if query and chapter.number:
            #     if str(query).lower() not in str(chapter.number).lower():
            #         continue
            self.chapters_column.controls.append(
                ft.ListTile(
                    title=ft.Text(chapter.number if len(str(chapter.number)) and chapter.number is not None else chapter.title, tooltip=chapter.title),
                    trailing=btn_read,
                    autofocus=chapter.id == self.chapter.id,
                    selected=chapter.id == self.chapter.id,
                    on_click=lambda e, chapter=chapter: self.change_chapter(chapter),
                    leading= ft.IconButton(ft.icons.DOWNLOAD_OUTLINED, on_click=lambda e, source=self.source, chapter=chapter: self.dl.download_chapter(self.manga, source, chapter), ),
                    key=chapter.id
                )
            )
        self.load_drawer()
        self.dl: DownloadManager = page.data['dl']
        self.content = None
        self.create_content()

    def focus_drawer(self):
        count = 0
        is_counting = False
        for list_tile in reversed(self.chapters_column.controls):
            if is_counting:
                count += 1
            if count == 8:
                try:
                    self.chapters_column.scroll_to(key=list_tile.key)
                except:
                    print('nothing happened kkkk')
            if list_tile.key == self.chapter.id:
                is_counting = True
                continue

    def load_drawer(self):
        readeds = self.db.is_each_readed(self.source, self.manga.id, self.manga.source_id if self.manga.source_id != 'opex' else 'opex', self.chapters)
        for list_tile, is_readed in zip(reversed(self.chapters_column.controls), reversed(readeds)):
            if is_readed:
                list_tile.trailing.icon = ft.icons.CHECK
            else:
                list_tile.trailing.icon = ft.icons.REMOVE
            if list_tile.key == self.chapter.id:
                list_tile.selected = True
                list_tile.autofocus = True
                continue
            list_tile.selected = False
            list_tile.autofocus = False

    def togle_readed(self, source, manga: Favorite, chapter: Chapter, language: str=None):
        if self.db.is_readed(source, manga.id, manga.source_id, chapter.id, language):
            self.db.delete_all_readed_above(manga, source, chapter, self.chapters, language)
        else:
            self.db.add_all_readed_below(manga, source, chapter, self.chapters, language)
        each_readed = self.db.is_each_readed(source, manga.id, manga.source_id, self.chapters)
        icon = ft.icons.REMOVE
        for is_read, btn in zip(each_readed, self.btns_list):
            if is_read:
                icon = ft.icons.CHECK
            btn.icon = icon
        self.page.update()

    def create_content(self):
        self.pages = self.page.data['chapter_images']
        self.pages_len = len(self.pages)
        self.pages = EnableBackwardIterator(iter(self.pages))
        self.currently_page = ft.Text(f' 1/{self.pages_len}')
        self.panel = ft.Image(src_base64=self.pages.next(), fit=ft.ImageFit.FIT_HEIGHT, height=self.page.height)
        self.page.window_full_screen = True
        self.page.title = f'{self.manga.name} - {self.chapter.number} {' > ' + self.chapter.title if self.chapter.title else ''}'  
        self.page.banner.visible = False
        if not self.db.is_readed(self.source, self.manga.id, self.manga.source_id if self.manga.source_id != 'opex' else 'opex', self.chapter.id):
            self.db.add_all_readed_below(self.manga, self.source, self.chapter, self.chapters, self.language)
        self.btn_next_chapter = ft.IconButton(ft.icons.NAVIGATE_NEXT_SHARP, on_click=lambda e: self.change_chapter())
        self.btn_next_chapter.visible = True if self.pages_len == 1 \
            and not self.chapters[0].id == self.chapter.id else False
        is_second_time = False
        if self.content != None:
            is_second_time = True
        self.image_row = ft.Row(
            [self.panel],
            alignment=ft.MainAxisAlignment.CENTER
        )
        self.content = ft.Stack([
            ft.Row([
                self.image_row,                
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row(
                [
                    self.btn_next_chapter,
                    ft.Card(ft.Row([self.currently_page], alignment=ft.MainAxisAlignment.CENTER), height=30, width=50,
                            opacity=0.5), ft.Container(width=10)],
                alignment=ft.MainAxisAlignment.END,
            )
        ])
        def next_page(e=None):
            if self.pages.i == self.pages_len:
                return
            self.panel.src_base64 = self.pages.next()
            self.panel.height = self.page.height
            self.currently_page.value = f'{self.pages.i}/{self.pages_len}'
            if self.pages.i == self.pages_len and \
                not self.chapters[0].id == self.chapter.id:
                self.btn_next_chapter.visible = True
            self.page.update()

        def prev_page(e=None):
            if self.pages.i == 1:
                return
            self.panel.src_base64 = self.pages.prev()
            self.panel.height = self.page.height
            self.currently_page.value = f'{self.pages.i}/{self.pages_len}'
            self.page.update()

        keybinds = self.db.get_config()['keybinds']

        def on_key(e: ft.KeyboardEvent):
            if e.key == keybinds['next-page']:
                next_page()
            if e.key == keybinds['previous-page']:
                prev_page()
            if e.key == keybinds['full-screen']:
                if self.page.window_full_screen:
                    self.page.window_full_screen = False
                else:
                    self.page.window_full_screen = True
            if e.key == 'F3':
                if not self.drawer.open:
                    self.page.show_end_drawer(self.drawer)
                    self.focus_drawer()
                else:
                    self.drawer.open = False
            if e.key == 'Escape':
                if self.page.window_full_screen:
                    self.page.window_full_screen = False
            if e.key == keybinds['return-home']:
                self.drawer.open = False
                self.page.update()
                self.page.title = f'MangaYouKnow {self.page.data['version']}' 
                self.page.go('/favorites') if not self.page.data['is_index'] else self.page.go('/')
                self.page.scroll = ft.ScrollMode.ADAPTIVE
                self.page.window_full_screen = False
                self.page.data['MangaOpen']()
            self.page.update()

        def resize(e):
            self.panel.height = float(e.control.height)
            self.page.update()

        self.content.data = {
            'resize': resize
        }
        if is_second_time:
            self.page.data['reader_container'].content = self.content
        else:
            self.page.on_keyboard_event = on_key
        self.page.update()

    def return_content(self):
        return self.content

    def change_chapter(self, chapter: Chapter=None):
        self.image_row.controls = [ft.ProgressRing(width=120, height=120)]
        self.page.update()
        if chapter:
            self.chapter = chapter
            self.drawer.open = False
            self.page.update()
        else:
            chapter_id = None
            for i, chapter in enumerate(reversed(self.chapters), 1):
                if chapter.id == self.chapter.id:
                    if len(self.chapters) == i:
                        print('no more chapters')
                        return False
                    self.chapter = list(reversed(self.chapters))[i]
                    chapter_id = self.chapter.id
                    break
            if chapter_id == None:
                return False
        self.load_drawer()
        pages = self.dl.get_chapter_image_urls(self.source, self.chapter.id)
        if not pages:
            return False
        images_b64 = self.dl.get_base64_images(pages)
        self.page.data['chapter_images'] = images_b64
        self.create_content()
        self.page.update()
        self.page.data['pre_load'](self.chapter)
