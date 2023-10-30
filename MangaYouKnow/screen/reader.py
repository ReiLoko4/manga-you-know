import flet as ft
import base64
import requests
from threading import Thread
from backend.database import DataBase
from backend.manager import ThreadManager, Downloader


class MangaReader:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = DataBase()
        self.dl = Downloader()
        self.content = None
        self.create_content()

    def create_content(self):
        self.page.banner.visible = False
        if not self.db.is_readed(self.page.data['source'], self.page.data['manga_id'], self.page.data['chapter_id']):
            self.db.add_readed(self.page.data['source'], self.page.data['manga_id'], self.page.data['chapter_id'])
        self.chapters = self.page.data['manga_chapters']
        self.pages = self.page.data['chapter_images']
        self.page.window_full_screen = True
        self.pages_len = len(self.pages)
        self.currently_page = ft.Text(f' 1/{self.pages_len}')
        self.panel = ft.Image(src_base64=self.pages[0], fit=ft.ImageFit.FIT_HEIGHT, height=self.page.height)
        self.btn_next_chapter = ft.IconButton(ft.icons.NAVIGATE_NEXT_SHARP, on_click=self.next_chapter)
        self.btn_next_chapter.visible = False
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
        def next(e=None):
            for i, img in enumerate(self.pages):
                if self.panel.src_base64 == img:
                    if self.pages_len > i + 1:
                        self.panel.src_base64 = self.pages[i + 1]
                        self.panel.height = self.page.height
                        self.currently_page.value = f'{i + 2}/{self.pages_len}'
                        if self.pages_len == i + 2:
                        #     self.db.set_manga(self.page.data['id'], 'id_last_readed', self.page.data['id_chapter'])
                            if not self.chapters[0]['id'] == self.page.data['chapter_id']:
                                self.btn_next_chapter.visible = True
                    break
            self.page.update()

        def previous(e=None):
            for i, img in enumerate(self.pages):
                if self.panel.src_base64 == img:
                    if i != 0:
                        self.panel.src_base64 = self.pages[i - 1]
                        self.panel.height = self.page.height
                        self.currently_page.value = f'{i}/{self.pages_len}'
                    break
            self.page.update()

        keybinds = self.db.get_config()['keybinds']

        def on_key(e: ft.KeyboardEvent):
            if e.key == keybinds['next-page']:
                next()
            if e.key == keybinds['previous-page']:
                previous()
            if e.key == keybinds['full-screen']:
                if self.page.window_full_screen:
                    self.page.window_full_screen = False
                else:
                    self.page.window_full_screen = True
            if e.key == 'Escape':
                if self.page.window_full_screen:
                    self.page.window_full_screen = False
            if e.key == keybinds['return-home']:
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
            if chapter['id'] == self.page.data['chapter_id']:
                if len(self.chapters) == i + 1:
                    print('no more chapters')
                    return False
                self.page.data['chapter_id'] = self.chapters[i + 1]['id']
                chapter_id = self.chapters[i + 1]['id']
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
