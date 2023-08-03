import flet as ft
import base64
import requests
from backend.downloader.mangalivre import MangaLivreDl



class MangaReader:
    def __init__(self, page: ft.Page):
        self.page = page
        self.pages = page.data['chapter_images']
        self.images_b64 = []
        for image in self.pages:
            response = requests.get(image['legacy'])
            self.images_b64.append(base64.b64encode(response.content).decode('utf-8'))
        self.images = [ft.Image(src_base64=i, fit=ft.ImageFit.FIT_HEIGHT, height=page.height) for i in self.images_b64]
        self.content = ft.Row([
            ft.Stack(
                self.images
            )],
            alignment=ft.MainAxisAlignment.CENTER
        )
        page.banner.visible = False
        for i, img in enumerate(self.images):
            if i != 0:
                img.visible = False
        def next(e=None):
            for i, img in enumerate(self.images):
                if img.visible:
                    if len(self.images) > i+1:
                        img.visible = False
                        self.images[i+1].visible = True
                        self.images[i+1].height = self.page.height
                    break
            page.update()
        def back(e=None):
            for i, img in enumerate(self.images):
                if img.visible:
                    if i != 0:
                        img.visible = False
                        self.images[i-1].visible = True
                    break
            page.update()
        def on_key(e: ft.KeyboardEvent):
            if e.key == 'Arrow Right':
                next()
            if e.key == 'Arrow Left':
                back()
            if e.key == 'F11':
                if page.window_full_screen:
                    page.window_full_screen = False
                else:
                    page.window_full_screen = True
            page.update()
        page.on_keyboard_event = on_key
        def resize(e):
            for i in self.images:
                if i.visible:
                    i.height = float(e.control.height)
            page.update()
        self.content.data = {
            'resize': resize
        }
        
    def return_content(self):
        return self.content


                
            
