import flet as ft
from backend.database import DataBase
from backend.managers import DownloadManager
from backend.models import Chapter


database = DataBase()


def MangaOpen(
        manga_info: dict,
        source_languages: dict,
        togle_notify: callable,
        page: ft.Page,
        is_index: bool = False,
        cards_row: ft.Row = None,
        mangas_card_notify: callable = None
    ) -> ft.AlertDialog:
    dl: DownloadManager = page.data['dl']
    manga_title = ft.Text(manga_info['name'] if len(manga_info['name']) < 35 else f'{manga_info['name'][0:33]}...', tooltip=manga_info['name'])
    def read(source, manga, chapter: Chapter, chapters: list[dict], language: str=None) -> None:
        manga_title.value = manga_info['name'] if len(manga_info['name']) < 25 else f'{manga_info['name'][0:22]}...'
        status = ft.Text('Buscando as imagens...', weight=ft.FontWeight.W_500)
        page.dialog.content = ft.Container(
            ft.Column([
                ft.Row([
                    ft.Image(manga['cover'], height=200, fit=ft.ImageFit.FIT_HEIGHT, border_radius=10),
                    ft.Text(f'Capítulo {chapter.number} - {chapter.title}' if chapter.title else f'Capítulo {chapter.number}', size=20, weight=ft.FontWeight.BOLD),
                ]),
                ft.Container(height=5),
                ft.Divider(height=5, color=ft.colors.GREY_700, thickness=2),
                ft.Container(height=5),
                ft.Row([
                    ft.ProgressRing(height=140, width=140),
                ],  alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([status], expand=True,alignment=ft.MainAxisAlignment.CENTER),
                ft.Text('Pressione F4 para sair do capítulo', size=15, weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )
        page.update()
        pages = dl.get_chapter_image_urls(source, chapter.id)
        status.value = 'Baixando as imagens...'
        page.update()
        images_b64 = dl.get_base64_images(pages)
        status.value = 'Pronto!'
        page.update()
        page.data['chapter_images'] = images_b64
        page.data['manga_chapters'] = chapters
        page.data['chapter_title'] = f'{chapter.title} - {chapter.number}' if chapter.title else chapter.number
        page.data['manga_name'] = manga['name']
        page.data['manga_id'] = manga['id']
        page.data['manga_source_id'] = manga[source] if source != 'opex' else source
        page.data['chapter_id'] = chapter.id
        page.data['source'] = source
        if language:
            page.data['language'] = language
        page.data['is_index'] = False
        if is_index:
            page.data['is_index'] = True
        page.go('/reader')
    btn_is_readed_list = []
    def togle_readed(source, manga, chapter_id, language: str=None):
        if database.is_readed(source, manga['id'], manga[source] if source != 'opex' else source, chapter_id, language if language else None):
            database.delete_readed(source, manga['id'], manga[source] if source != 'opex' else source, chapter_id, language if language else None)
        else:
            database.add_readed(source, manga['id'], manga[source] if source != 'opex' else source, chapter_id, language if language else None)
        each_readed = database.is_each_readed(source, manga['id'], manga[source] if source != 'opex' else source, chapters_by_source[f'{source}_{language_options.value}'])
        icon = ft.icons.REMOVE
        for i, btn in enumerate(btn_is_readed_list):
            if each_readed[i]:
                icon = ft.icons.CHECK
            btn.icon = icon
        if is_index:
            cards_row.controls = mangas_card_notify(cards_row, page)
        page.update()
    chapter_search = ft.TextField(
        label='Capítulo...',
        width=240,
        border_radius=20,
        height=40,
        border_color=ft.colors.GREY_700,
        focused_border_color=ft.colors.BLUE_300
    )
    list_chapters = ft.Column(height=8000, width=240, scroll='always')
    sources = [i for i in list(manga_info.keys()) if i.endswith('_id') and manga_info[i] != None]
    options = []
    is_op = False
    for source in sources:
        match source:
            case 'md_id':
                text = 'MangaDex'
            case 'ml_id':
                text = 'MangaLivre'
            case 'ms_id':
                text = 'MangaSee'
            case 'mc_id':
                text = 'MangasChan'
            case 'mf_id':
                text = 'MangaFire'
            case 'mx_id':
                text = 'MangaNexus'
            case 'gkk_id':
                text = 'Gekkou Scans'
            case 'tsct_id':
                text = 'Taosect Scans'
            case 'tcb_id':
                text = 'TCB Scans'
            case 'op_id':
                text = 'OP Scans'
            case 'lmorg_id':
                text = 'LerManga.org'
        options.append(ft.dropdown.Option(source, text))
        if manga_info[source] in [
            '5/one-piece',
            'One-Piece',
            'one-piece',
            13,
            '13',
            'dkw',
            'a1c7c817-4e59-43b7-9365-09675a149a6f',
        ] and not is_op:
            is_op = True
            options.append(ft.dropdown.Option('opex', 'One Piece Ex'))
    chapters_by_source = {}
    source_options = ft.Dropdown(
        options=options,
        width=140,
        value=sources[0]
    )
    language_options = ft.Dropdown(
        options=[ft.dropdown.Option(i, i) for i in source_languages[source_options.value]],
        width=140,
        value=source_languages[source_options.value][0]
    )
    if len(sources) == 1:
        source_options.disabled = True
    if len(source_languages[source_options.value]) == 1:
        language_options.disabled = True
    
    def load_chapters(query: str=None) -> None:
        btn_is_readed_list.clear()
        language_options.options = [ft.dropdown.Option(i, i) for i in source_languages[source_options.value]]
        if len(source_languages[source_options.value]) == 1:
            language_options.value = source_languages[source_options.value][0]
            language_options.disabled = True
        source_options.disabled = True
        language_options.disabled = True
        download_all.disabled = True
        if not query: chapter_search.disabled = True
        list_chapters.controls = [
            ft.Row(
                [
                    ft.ProgressRing(height=120, width=120)
                ], alignment=ft.MainAxisAlignment.CENTER, width=230
            )
        ]
        page.update()
        if chapters_by_source.get(f'{source_options.value}_{language_options.value}'):
            chapters: list[Chapter] = chapters_by_source[f'{source_options.value}_{language_options.value}']
        else:
            chapters = dl.get_chapters(source_options.value, manga_info.get(source_options.value) if source_options.value != 'opex' else None) if len(source_languages[source_options.value]) == 1 \
                else dl.get_chapters(source_options.value, manga_info[source_options.value], language_options.value) 
            chapters_by_source[f'{source_options.value}_{language_options.value}'] = chapters
        list_chapters.controls = []
        is_each_readed = database.is_each_readed(
            source_options.value, 
            manga_info['id'],
            manga_info.get(source_options.value) 
            if source_options.value != 'opex' else source, 
            chapters
        )
        icon = ft.icons.REMOVE
        if not chapters:
            list_chapters.controls = [
                ft.ListTile(
                    title=ft.Text(
                        'Nenhum capítulo encontrado nesse idioma, jovem!' if query == None else f'Nenhum resultado para "{query}"'
                    ),
                )
            ]
            if len(source_languages[source_options.value]) > 1:
                language_options.disabled = False
            if len(sources) > 1:
                source_options.disabled = False
            page.update()
            return
        for i, chapter in enumerate(chapters):
            if is_each_readed[i]:
                icon = ft.icons.CHECK
            btn_read = ft.IconButton(icon, on_click=lambda e, source=source_options.value, manga=manga_info, chapter_id=chapter.id, language=language_options.value: togle_readed(source, manga, chapter_id, language if len(source_languages[source_options.value]) > 1 else None))
            btn_is_readed_list.append(btn_read)
            if query and chapter.number:
                if str(query).lower() not in str(chapter.number).lower():
                    continue
            list_chapters.controls.append(
                ft.ListTile(
                    title=ft.Text(chapter.number if chapter.number else chapter.title, tooltip=chapter.title),
                    trailing=btn_read, 
                    leading= ft.IconButton(ft.icons.DOWNLOAD_OUTLINED, on_click=lambda e, source=source_options.value, chapter=chapter: dl.download_chapter(manga_info, source, chapter)),
                    on_click=lambda e, source=source_options.value, chapter=chapter: read(source, manga_info, chapter, chapters, language_options.value if len(source_languages[source_options.value]) > 1 else None),
                    key=chapter.id
                )
            )
        if len(source_options.options) > 1:
            source_options.disabled = False
        if len(source_languages[source_options.value]) > 1:
            language_options.disabled = False
        download_all.disabled = False
        chapter_search.disabled = False
        last_readed = database.get_last_readed(manga_info['id'])
        # list_chapters.scroll_to(key=last_readed['chapter_id'] if last_readed else None)
        page.update()
    download_all = ft.ElevatedButton(
        text='Baixar tudo',
        on_click=lambda e: dl.download_all_chapters(manga_info, source_options.value, chapters_by_source[f'{source_options.value}_{language_options.value}']))
    switch = ft.Switch(
        value=database.is_notify(manga_info['id']),
        width=50,
        height=30,
        label='Notificações',
        label_position=ft.LabelPosition.RIGHT,
    )
    switch.on_change=lambda e: togle_notify(e, manga_info)
    source_options.on_change = lambda e: load_chapters()
    language_options.on_change = lambda e: load_chapters()
    chapter_search.on_change = lambda e: load_chapters(e.control.value if e.control.value != '' else None)
    def close(_=None):
        list_chapters.controls = []
        alert.open = False
        page.update()
    alert = ft.AlertDialog(
        title=ft.Row([manga_title, ft.IconButton(ft.icons.CLOSE, on_click=close)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        content=ft.Container(
            ft.Row([
                ft.Column([
                    ft.Container(ft.Image(manga_info['cover'], height=250, fit=ft.ImageFit.FIT_HEIGHT, border_radius=10), padding=5),
                    source_options,
                    language_options,
                    switch,
                    download_all,
                ]),
                ft.Column([
                    chapter_search,
                    ft.Card(list_chapters, width=250, height=420)
                ])
            ]), height=500, width=430
        )
    )
    page.dialog = alert
    alert.open = True
    page.update()
    load_chapters()
