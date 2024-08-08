import flet as ft
from backend.database import DataBase

class Configs:
    def __init__(self, page: ft.Page):
        database = DataBase()
        configs = database.get_config()
        pick_directory_dialog = ft.FilePicker()
        download_path = ft.TextField(read_only=True, value=configs['download-path'])
        def change_keybind(_=None):
            keybinds = database.get_config()['keybinds']
            def listen_key(btn:ft.TextButton):
                btn.text = '...'
                page.update()
            full_screen = ft.TextButton(keybinds['full-screen'], disabled=True)
            full_screen.on_click = lambda e, btn=full_screen: listen_key(btn)
            return_home = ft.TextButton(keybinds['return-home'], disabled=True)
            return_home.on_click = lambda e, btn=return_home: listen_key(btn)
            next_page = ft.TextButton(keybinds['next-page'], disabled=True)
            next_page.on_click = lambda e, btn=next_page: listen_key(btn)
            previous_page = ft.TextButton(keybinds['previous-page'], disabled=True)
            previous_page.on_click = lambda e, btn=previous_page: listen_key(btn)
            change_keys = ft.AlertDialog(
                title=ft.Text('EM BREVE!'),
                content=ft.Column([
                    ft.Card(ft.Row([full_screen, ft.Text('Tela cheia')], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), margin=1),
                    ft.Card(ft.Row([return_home, ft.Text('Voltar para o home')], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), margin=1),
                    ft.Card(ft.Row([next_page, ft.Text('Passar página')], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), margin=1),
                    ft.Card(ft.Row([previous_page, ft.Text('Voltar página')], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), margin=1),
                ])
            )
            page.dialog = change_keys
            change_keys.open = True
            page.update()
        def pick_files_result(e: ft.FilePickerResultEvent):
            if e.path:
                download_path.value = e.path
                database.set_config('download-path', e.path)
                download_path.update()
        pick_directory_dialog.on_result = pick_files_result
        page.overlay.append(pick_directory_dialog)
        def change_theme(theme: str):
            database.set_config('theme-mode', theme)
            page.theme_mode = theme
            page.banner.bgcolor = ft.colors.GREY_900 if theme == 'dark' else ft.colors.GREY_200
            page.update()
        self.content = ft.Row(
            [   
                ft.Column([
                    ft.TextButton('Mudar keybinds', on_click=change_keybind),
                    ft.Text('Tema'),
                    ft.RadioGroup(ft.Column([
                        ft.Radio(label='Claro', value='light'),
                        ft.Radio(label='Escuro', value='dark'),
                    ]), on_change=lambda e: change_theme(e.control.value), 
                    value=configs['theme-mode']
                    ),
                    ft.Text('Pasta de download'),
                    download_path,
                    ft.ElevatedButton(
                        'Escolher pasta',
                        icon=ft.icons.UPLOAD_FILE,
                        on_click=lambda _: pick_directory_dialog.get_directory_path(
                            'Escolha a pasta de download',
                        ),
                    ),
                ])
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            width=1300
        )

    def return_content(self):
        return self.content
