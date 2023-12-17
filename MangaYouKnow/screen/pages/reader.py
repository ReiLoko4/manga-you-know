import flet as ft
from backend.models import Chapter
from backend.database import DataBase
from backend.managers import DownloadManager
from backend.utilities import EnableBackwardIterator


class MangaReader:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = DataBase()
        self.dl: DownloadManager = page.data['dl']
        self.content = None
        self.create_content()

    def create_content(self):
        self.page.title = f'{self.page.data['manga_name']} - {self.page.data['chapter_title']}' 
        self.page.banner.visible = False
        if not self.db.is_readed(self.page.data['source'], self.page.data['manga_id'], self.page.data['manga_source_id'], self.page.data['chapter_id']):
            self.db.add_readed(self.page.data['source'], self.page.data['manga_id'], self.page.data['manga_source_id'], self.page.data['chapter_id'])
        self.chapters: list[Chapter] = self.page.data['manga_chapters']
        self.pages = self.page.data['chapter_images']
        self.pages_len = len(self.pages)
        self.pages = EnableBackwardIterator(iter(self.pages))
        self.page.window_full_screen = True
        self.currently_page = ft.Text(f' 1/{self.pages_len}')
        self.panel = ft.Image(src_base64=self.pages.next(), fit=ft.ImageFit.FIT_HEIGHT, height=self.page.height)
        self.btn_next_chapter = ft.IconButton(ft.icons.NAVIGATE_NEXT_SHARP, on_click=self.next_chapter)
        self.btn_next_chapter.visible = True if self.pages_len == 1 \
            and not self.chapters[0].id == self.page.data['chapter_id'] else False
        is_second_time = False
        if self.content != None:
            is_second_time = True
        self.image_row = ft.Row(
            [self.panel],
            alignment=ft.MainAxisAlignment.CENTER
        )
        self.content = ft.Stack([
            self.image_row,                
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
                not self.chapters[0].id == self.page.data['chapter_id']:
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
            if e.key == 'Escape':
                if self.page.window_full_screen:
                    self.page.window_full_screen = False
            if e.key == keybinds['return-home']:
                self.page.title = f'MangaYouKnow {self.page.data['version']}' 
                self.page.go('/favorites')
                self.page.scroll = ft.ScrollMode.ADAPTIVE
                self.page.window_full_screen = False
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

    def return_content(self):
        return self.content

    def next_chapter(self, _=None):
        self.image_row.controls = [ft.ProgressRing(width=120, height=120)]
        self.page.update()
        self.chapters.reverse()
        chapter_id = None
        for i, chapter in enumerate(self.chapters):
            if chapter.id == self.page.data['chapter_id']:
                if len(self.chapters) == i + 1:
                    print('no more chapters')
                    return False
                self.page.data['chapter_id'] = self.chapters[i + 1].id
                self.page.data['chapter_title'] = f'{chapter.title} - {chapter.number}' if chapter.title else chapter.number
                chapter_id = self.chapters[i + 1].id
                break
        self.chapters.reverse()
        if chapter_id == None:
            return False
        pages = self.dl.get_chapter_image_urls(self.page.data['source'], chapter_id)
        if not pages:
            print('errokkkkk')
            return False
        images_b64 = self.dl.get_base64_images(pages)
        self.page.data['chapter_images'] = images_b64
        self.create_content()
        self.page.update()
