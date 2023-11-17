import flet as ft
from pathlib import Path
from updater import Updater
from os import startfile


updater = Updater()


def launch(page: ft.Page) -> ft.FletApp:
    page.title = 'MangaYouKnow Launcher'
    page.theme_mode = 'dark'
    page.window_width = 700
    page.window_height = 600
    page.window_max_width = 700
    page.window_max_height = 600
    page.window_resizable = False
    page.vertical_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE
    options_releases = ft.Dropdown(visible=False)
    local_release = updater.get_local_release()
    if not updater.is_downloaded(local_release):
        updater.set_version('none')
        local_release = 'none'
    if local_release == 'none':
        releases = updater.get_releases()
        options_releases.options = \
            [ft.dropdown.Option(release['tag_name'], release['tag_name']) for release in releases[:-3]]
        options_releases.value = releases[0]['tag_name']
        options_releases.data = {release['tag_name']: release for release in releases}
        options_releases.visible = True
    else:
        latest_release = updater.get_latest_release()
        if local_release != latest_release['tag_name']:
            column = ft.Column(height=500, alignment=ft.MainAxisAlignment.CENTER)
            def download_latest(_=None):
                column.controls.append(ft.ProgressRing(height=40, color='red'))
                page.update()
                latest_link = [
                    i['browser_download_url'] for i in latest_release['assets'] \
                        if latest_release['tag_name'] in i['browser_download_url']
                ][0]
                updater.download_release(latest_link, latest_release['tag_name'])
                startfile(Path('app') / f'{latest_release["tag_name"]}.exe')
                page.window_destroy()
            def cancel(_=None):
                startfile(Path('app') / f'{local_release}.exe')
                page.window_destroy()
            yes_btn = ft.ElevatedButton('Sim', on_click=download_latest)
            column.controls = [
                ft.Text('Baixar nova versão?'),
                ft.Text(f'Versão atual: {local_release}'),
                ft.Text(f'Versão mais recente: {latest_release["tag_name"]}'),
                ft.Row([
                    yes_btn,
                    ft.ElevatedButton('Não', on_click=cancel)
                ]),
            ]
            page.add(
                ft.Row([
                    column
                ], alignment=ft.MainAxisAlignment.CENTER)
            )
            page.update()
            return
        else:
            startfile(Path('app') / f'{local_release}.exe')
            page.window_destroy()
            return
    progress_bar = ft.ProgressBar(visible=False, height=30, color='red')
    def download(_=None):
        progress_bar.visible = True
        updater.download_release(options_releases.data[options_releases.value]['assets'][0]['browser_download_url'], 
            options_releases.value, progress_bar)
        startfile(Path('app') / f'{options_releases.value}.exe')
        page.window_destroy()

    download_btn = ft.ElevatedButton('Download', on_click=download)
    page.add(
        ft.Row([
            ft.Column([
                options_releases,
                ft.Row([
                download_btn,
                progress_bar])
            ], alignment=ft.MainAxisAlignment.CENTER, height=500
            )], alignment=ft.MainAxisAlignment.CENTER
        )
    )
    page.update()

def __main__():
    local_release = updater.get_local_release()
    is_downloaded = updater.is_downloaded(local_release)
    latest_release = updater.get_latest_release()
    if local_release == latest_release['tag_name'] and is_downloaded:
        startfile(Path('app') / f'{local_release}.exe')
        return
    ft.app(target=launch)
