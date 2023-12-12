import flet as ft
from time import sleep
from backend.models import Manga
from backend.database import DataBase
from backend.managers import DownloadManager
from screen.components import MangasCardNotify


class Index:
    def __init__(self, page: ft.Page):
        connection_data = DataBase()
        downloader: DownloadManager = page.data['dl']
        source_selector = ft.Dropdown(options=[
            ft.dropdown.Option('md', text='MangaDex'),
            ft.dropdown.Option('ml', text='MangaLivre'),
            ft.dropdown.Option('ms', text='MangaSee'),
            ft.dropdown.Option('mc', text='MangasChan'),
            ft.dropdown.Option('mf', text='MangaFire'),
            ft.dropdown.Option('mx', text='MangaNexus'),
            ft.dropdown.Option('gkk', text='Gekkou'),
            ft.dropdown.Option('tsct', text='Taosect'),
            ft.dropdown.Option('tcb', text='TCB'),
            # ft.dropdown.Option('lmorg', text='LerManga.org'),
            # ft.dropdown.Option('op', text='OP Scans'),
        ], value='md', width=140)

        local_search = [
            'ms'
        ]
        results = ft.Column(width=470, spacing=0.7, data={'last_src': '', 'chapters': []})
        results_card = ft.Card(ft.Container(results), color='gray', visible=False)
        search = ft.TextField(
            label='Pesquisar Mangás...',
            width=500,
            border_radius=20,
            border_color=ft.colors.GREY_700,
            focused_border_color=ft.colors.BLUE_300,
        )
        index = ft.Stack(width=1300, height=1000)
        manga = ft.Row(visible=False)
        self.is_clicked = False

        def togle_favorite(manga: Manga, button: ft.IconButton, is_on_search: bool = False):
            if connection_data.is_favorite(f'{source_selector.value}_id', manga.id):
                if connection_data.delete_manga_by_key(f'{source_selector.value}_id', manga.id):
                    button.icon = ft.icons.BOOKMARK_OUTLINE
            else:
                if connection_data.add_manga(
                    manga,
                    md_id=manga.id if source_selector.value == 'md' else None,
                    ml_id=manga.id if source_selector.value == 'ml' else None,
                    ms_id=manga.id if source_selector.value == 'ms' else None,
                    mc_id=manga.id if source_selector.value == 'mc' else None,
                    mf_id=manga.id if source_selector.value == 'mf' else None,
                    mx_id=manga.id if source_selector.value == 'mx' else None,
                    gkk_id=manga.id if source_selector.value == 'gkk' else None,
                    tsct_id=manga.id if source_selector.value == 'tsct' else None,
                    tcb_id=manga.id if source_selector.value == 'tcb' else None,
                    op_id=manga.id if source_selector.value == 'op' else None,
                    lmorg_id=manga.id if source_selector.value == 'lmorg' else None,
                ):
                    button.icon = ft.icons.BOOKMARK_ROUNDED
            page.update()
            if is_on_search:
                self.is_clicked = True
                sleep(1)
                self.is_clicked = False
                search.focus()
                page.update()

        def manga_page(info_manga: Manga):
            button_favorite = ft.IconButton(
                ft.icons.BOOKMARK_ROUNDED if connection_data.is_favorite(f'{source_selector.value}_id', info_manga.id) else ft.icons.BOOKMARK_OUTLINE,
                height=30)
            button_favorite.on_click = lambda e, info=info_manga, button=button_favorite: togle_favorite(info, button)
            manga_dialog = ft.AlertDialog(
                title=ft.Text(info_manga.name[0:30], tooltip=info_manga.name),
                content=ft.Row([
                    ft.Image(src=info_manga.cover, height=400, width=ft.ImageFit.FIT_HEIGHT, animate_size=300,
                             border_radius=ft.border_radius.all(30)),
                ]),
                actions=[button_favorite]
            )
            manga_dialog.open = True
            page.dialog = manga_dialog
            page.update()

        def search_mangas(e: ft.ControlEvent = None):
            query = e
            if not type(e) == str:
                query = e.control.value
            if len(query) == 0:
                results.controls.clear()
                results_card.visible = False
                page.update()
                return False
            results.controls.clear()
            results.controls.append(
                ft.ListTile(
                    key='noresult',
                    title=ft.Row([ft.Text('Procurando...'), ft.ProgressRing()],
                                 alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    disabled=True,
                    height=55
                )
            )
            results_card.visible = True
            page.update()
            response = downloader.search(source_selector.value, query, results.data['chapters'] if results.data['last_src'] == source_selector.value else None)
            if query != search.value:
                    return False
            if source_selector.value in local_search:
                results.data['chapters'] = response[1]
                response = response[0]
                results.data['last_src'] = source_selector.value
            favorites = connection_data.get_database()
            list_favorites_id = [i[f'{source_selector.value}_id'] for i in favorites]
            results_card.visible = True
            results.controls.clear()
            if not response:
                results.controls.append(
                    ft.ListTile(
                        key='noresult',
                        title=ft.Text('Nenhum mangá encontrado!'),
                        disabled=True,
                        height=55
                    )
                )
            else:
                for manga in response:
                    button_favorite = ft.IconButton(ft.icons.BOOKMARK_ROUNDED if manga.id in list_favorites_id else ft.icons.BOOKMARK_OUTLINE, height=30)
                    button_favorite.on_click = lambda e, manga=manga, button=button_favorite: togle_favorite(manga, button, True)
                    results.controls.append(
                        ft.ListTile(
                            key='manga',
                            title=ft.Text(f'{manga.name[0:42]}...' if len(manga.name) > 45 else manga.name[0:50], tooltip=manga.name),
                            height=45,
                            trailing=button_favorite,
                            on_click=lambda e, info=manga: manga_page(info)
                        )
                    )
                if len(search.value) == 0:
                    results.controls.clear()
                    results_card.visible = False
            page.update()

        def out_search(e):
            sleep(0.1)
            if self.is_clicked:
                return
            results_card.visible = False
            page.update()

        def focus_search(e):
            if len(results.controls) != 0:
                if results.controls[0].key == 'manga':
                    results_card.visible = True
                    page.update()
        def togle_visible(_:ft.ControlEvent=None):
            page.update()
            if search.value:
                search.focus()
                search_mangas(search.value)
        source_selector.on_change = togle_visible
        search.on_change = search_mangas
        search.on_blur = out_search
        search.on_focus = focus_search
        favorites_row = ft.Row(
            wrap=True,
            width=page.width - 90,
            height=10000,
            top=170
        )
        index.controls.append(
            favorites_row
        )
        index.controls.append(
            ft.Column([
            ft.ResponsiveRow([
                ft.Column([ft.Container(bgcolor='white', width=300)], col=2),
                ft.Column([ft.Container(search, padding=5)], col=6),
                ft.Column([ft.Container(ft.Row([source_selector]), width=250, padding=10)], col=4),
            ], alignment=ft.MainAxisAlignment.CENTER, columns=12),
            ft.ResponsiveRow([
                ft.Column([ft.Container(bgcolor='white', width=300)], col=2),
                ft.Column([ft.Container(results_card, padding=5)], col=6),
                ft.Column([ft.Container(width=250, padding=10)], col=4),
            ], alignment=ft.MainAxisAlignment.CENTER, columns=12),
            ], spacing=0.3)
        )
        stack = ft.Stack([
            index,
            manga
        ], width=1000, height=1000)
        self.content = ft.Column(
            [stack],
            scroll='always',
        )
        def update(e):
            if e:
                favorites_row.width = e
                stack.width = e
                index.width = e
                self.content.width = e
            favorites = MangasCardNotify(connection_data, page)
            count = 0
            for num in range(len(favorites)):
                if num % 3 == 0:
                    count += 1
            stack.height = count * 435
            index.height = count * 435
            favorites_row.height = count * 435
            if page.data['last_favorites'] == favorites:
                return
            favorites_row.controls = favorites
            page.update()

        def resize(e):
            favorites_row.width = float(e.control.width) - 90
            index.width = float(e.control.width) - 90
            stack.width = float(e.control.width) - 90
            self.content.width = float(e.control.width) - 90
            page.update()

        favorites_row.controls = MangasCardNotify(connection_data, page)
        self.content.data = [update, resize]

    def return_content(self) -> ft.Row:
        return self.content
