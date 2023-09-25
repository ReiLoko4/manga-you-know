import flet as ft
import base64
import requests
from threading import Thread

from backend.manager import ThreadManager
from backend.database import DataBase


class MangaReader:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = DataBase()
        self.content = None
        self.create_content()

    def create_content(self):
        self.chapters = self.page.data['manga_chapters']
        self.pages = self.page.data['chapter_images']

        self.images_b64 = []

        def get_base_64_image(url, index: int):
            response = requests.get(url)
            self.images_b64.append([base64.b64encode(response.content).decode('utf-8'), index])

        threads = ThreadManager()
        for i, image in enumerate(self.pages):
            threads.add_thread(
                Thread(
                    target=lambda url=image['legacy'], index=i: get_base_64_image(url, index)
                )
            )
        threads.start()
        threads.join()

        def to_sort(e):
            return e[1]

        self.images_b64.sort(key=to_sort)
        self.page.window_full_screen = True
        self.currently_page = ft.Text(f' 1/{len(self.images_b64)}')
        self.images = [ft.Image(src_base64=i[0], fit=ft.ImageFit.FIT_HEIGHT, height=self.page.height) for i in
                       self.images_b64]
        self.btn_next_chapter = ft.IconButton(ft.icons.NAVIGATE_NEXT_SHARP, on_click=self.next_chapter)
        self.btn_next_chapter.visible = False
        is_second_time = False
        if self.content != None:
            is_second_time = True
        self.content = ft.Stack([
            ft.Row(
                self.images,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.Row(
                [
                    self.btn_next_chapter,
                    ft.Card(ft.Row([self.currently_page], alignment=ft.MainAxisAlignment.CENTER), height=30, width=50,
                            opacity=0.5), ft.Container(width=10)],
                alignment=ft.MainAxisAlignment.END,
            )
        ])
        self.page.banner.visible = False
        for i, img in enumerate(self.images):
            if i != 0:
                img.visible = False

        def next(e=None):
            for i, img in enumerate(self.images):
                if img.visible:
                    if len(self.images) > i + 1:
                        img.visible = False
                        self.images[i + 1].visible = True
                        self.images[i + 1].height = self.page.height
                        self.currently_page.value = f'{i + 2}/{len(self.images)}'
                        if len(self.images) == i + 2:
                            self.db.set_manga(self.page.data['id'], 'id_last_readed', self.page.data['id_chapter'])
                            if not self.chapters[0]['id_chapter'] == self.page.data['id_chapter']:
                                self.btn_next_chapter.visible = True
                    break
            self.page.update()

        def previous(e=None):
            for i, img in enumerate(self.images):
                if img.visible:
                    if i != 0:
                        img.visible = False
                        self.images[i - 1].visible = True
                        self.currently_page.value = f'{i}/{len(self.images)}'
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
            for i in self.images:
                if i.visible:
                    i.height = float(e.control.height)
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
        self.chapters.reverse()
        chapter = None
        for i, chapter in enumerate(self.chapters):
            if str(chapter['id_chapter']) == str(self.page.data['id_chapter']):
                if len(self.chapters) == i + 1:
                    print('no more chapters')
                    return False
                self.page.data['id_chapter'] = self.chapters[i + 1]['id_chapter']
                chapter = self.chapters[i + 1]
                break
        if chapter == None:
            print('sem mais capitulos')
            return False
        manga_pages = self.dl.get_chapter_imgs(
            chapter['releases'][list(chapter['releases'].keys())[0]]['id_release'])

        if not manga_pages:
            print('errokkkkk')
            return False
        self.page.data['chapter_images'] = manga_pages
        self.chapters.reverse()
        self.create_content()
        self.page.update()
