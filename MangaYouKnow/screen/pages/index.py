import flet as ft
from time import sleep
from backend.models import Manga, Chapter
from backend.tables import Favorite, Readed
from backend.database import DataBase
from backend.managers import DownloadManager
from screen.components import MangasCardNotify, RelatoryCard


class Index:
    def __init__(self, page: ft.Page):
        database = DataBase()
        dl: DownloadManager = page.data['dl']
        manga_options = [
            ft.dropdown.Option('md', text='MangaDex'),
            # ft.dropdown.Option('ml', text='MangaLivre'),
            ft.dropdown.Option('ms', text='MangaSee'),
            ft.dropdown.Option('mc', text='MangasChan'),
            # ft.dropdown.Option('mf', text='MangaFire'),
            ft.dropdown.Option('mx', text='MangaNexus'),
            ft.dropdown.Option('gkk', text='Gekkou'),
            ft.dropdown.Option('tsct', text='Taosect'),
            ft.dropdown.Option('tcb', text='TCB'),
            # ft.dropdown.Option('lmorg', text='LerManga.org'),
            # ft.dropdown.Option('op', text='OP Scans'),
        ]
        anime_options = [
            ft.dropdown.Option('aon', text='AnimesOnNZ'),
            ft.dropdown.Option('ba', text='BetterAnime'),
            # ft.dropdown.Option('av', text='AnimesVision'),
            ft.dropdown.Option('af', text='AnimeFire'),
            # ft.dropdown.Option('ah', text='AnimesHouse'),
            ft.dropdown.Option('go', text='Goyabu'),   
            ft.dropdown.Option('ao', text='AnimesOnline'),
            # ft.dropdown.Option('oa', text='OtakuAnimes'),
        ]
        btn_relatory = ft.IconButton(
            ft.icons.ASSESSMENT_OUTLINED,
            tooltip='Gerar relatório'
        )
        btn_refresh = ft.IconButton(
            ft.icons.CACHED_OUTLINED,
            tooltip='Recarregar'
        )
        source_selector = ft.Dropdown(options=manga_options, value='md', width=140)
        favorite_type = ft.SegmentedButton(
            show_selected_icon=False,
            allow_multiple_selection=False,
            allow_empty_selection=False,
            segments=[
                ft.Segment('manga', label=ft.Text('Manga')),
                ft.Segment('anime', label=ft.Text('Anime')),
            ],
            selected={'manga'},
        )
        results = ft.Column(width=470, spacing=0.7)
        results_card = ft.Card(ft.Container(results, border=ft.border.all(1, 'white'), border_radius=15), color='gray', visible=False)
        search = ft.TextField(
            label=f'Pesquisar {list(favorite_type.selected)[0]}s...',
            width=500,
            border_radius=20,
            border_color=ft.colors.GREY_700,
            focused_border_color=ft.colors.BLUE_300,
        )
        # search = ft.SearchBar(
        #     bar_hint_text=f'Pesquisar {list(favorite_type.selected)[0]}s...',
        # )
        index = ft.Stack(width=1300, height=1000)
        manga = ft.Row(visible=False)
        self.is_clicked = False
        
        def get_relatory(_=None):
            relatory_row = ft.Row(
                [ft.ProgressRing(height=200, width=200, color=ft.colors.BLUE_500, key='progress')], 
                wrap=True, height=10000, alignment=ft.MainAxisAlignment.START, scroll='always'
            )
            def close_dialog(_=None):
                dialog.open = False
                page.update()
            dialog = ft.AlertDialog(
                title=ft.Row(
                    [ft.Text('Favoritos', size='xl'), ft.IconButton(ft.icons.CLOSE, on_click=close_dialog)],
                    expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                content=relatory_row
            )
            page.dialog = dialog
            dialog.open = True
            page.update()
            favorites_noty = database.get_favorites_notify()
            relatory_row.controls.clear()
            for favorite in favorites_noty:
                try:
                    relatory_row.controls.append(RelatoryCard(page, favorite))
                except Exception as e:
                    print(e)
            page.update()

        btn_relatory.on_click = get_relatory
        def change_options(e: ft.ControlEvent):
            source_selector.options = manga_options if list(e.control.selected)[0] == 'manga' else anime_options
            source_selector.value = source_selector.options[0].key
            search.label = f'Pesquisar {list(favorite_type.selected)[0]}s...'
            search_mangas(search.value)
            page.update()

        favorite_type.on_change = change_options
        def togle_favorite(manga: Manga, button: ft.IconButton, is_on_search: bool = False):
            if database.is_favorite(source_selector.value, manga.id):
                if database.delete_favorite_by_key(source_selector.value, manga.id):
                    button.icon = ft.icons.BOOKMARK_OUTLINE
            else:
                if database.add_favorite(manga, source_selector.value, manga.id, list(favorite_type.selected)[0]):
                    button.icon = ft.icons.BOOKMARK_ROUNDED
            page.update()
            if is_on_search:
                self.is_clicked = True
                sleep(0.1)
                search.focus()
                # results_card.visible = True
                # page.update()
                # sleep(1)
                self.is_clicked = False
                # search.focus()
                # page.update()

        def manga_page(info_manga: Manga):
            button_favorite = ft.IconButton(
                ft.icons.BOOKMARK_ROUNDED if database.is_favorite(source_selector.value, info_manga.id) else ft.icons.BOOKMARK_OUTLINE,
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
            if len(results.controls) == 0 or results.controls[0].key != 'noresult':
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
            response = dl.search(source_selector.value, query, list(favorite_type.selected)[0])
            if query != search.value:
                    return False
            favorites = database.get_favorites_by_source(source_selector.value)
            list_favorites_id = [i.source_id for i in favorites]
            results_card.visible = True
            results.controls.clear()
            if not response:
                results.controls.append(
                    ft.ListTile(
                        key='noresult',
                        title=ft.Text(f'Nenhum {'manga' if list(favorite_type.selected)[0] == 'manga' else 'anime'} encontrado!'),
                        disabled=True,
                        height=55
                    )
                )
                page.update()
                return
            results.data = response
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
                    favorites = database.get_favorites()
                    list_favorites_id = [i.source_id for i in favorites]
                    results.controls.clear()
                    for manga in results.data:
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
            top=120,
            scroll='always'
        )
        index.controls.append(
            favorites_row
        )
        index.controls.append(
            ft.Column([
            ft.Row([
                ft.Column([ft.Container(ft.Row([favorite_type, search, source_selector, btn_refresh, btn_relatory], alignment=ft.MainAxisAlignment.END))], height=70, alignment=ft.MainAxisAlignment.CENTER),
                # ft.Column([ft.Container(, padding=10)], col=6),
                # ft.Column([ft.Container(ft.Row([]), width=250, padding=10)], col=4),
                # ft.Column([ft.Container(ft.Row([]), padding=10)], col=2, height=70, width=250, alignment=ft.MainAxisAlignment.START),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.ResponsiveRow([
                ft.Column([ft.Container(bgcolor='white', width=300)], col=3),
                ft.Column([ft.Container(results_card, padding=5)], col=7),
                ft.Column([ft.Container(width=250, padding=10)], col=3),
            ], alignment=ft.MainAxisAlignment.CENTER, columns=13),
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
            favorites = MangasCardNotify(favorites_row, page)
            count = 1
            for num in range(len(favorites)):
                if num % 3 == 0:
                    count += 1
            stack.height = count * 800
            index.height = count * 800
            favorites_row.height = count * 800
            favorites_row.controls = favorites
            page.update()

        def resize(e):
            favorites_row.width = float(e.control.width) - 90
            index.width = float(e.control.width) - 90
            stack.width = float(e.control.width) - 90
            self.content.width = float(e.control.width) - 90
            page.update()
        self.content.data = [update, resize]

    def return_content(self) -> ft.Row:
        return self.content
