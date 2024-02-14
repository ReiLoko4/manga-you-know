import flet as ft
from backend.database import DataBase
from backend.managers import DownloadManager
from backend.models import Chapter, Episode
from backend.tables import Favorite
# from screen.utilities import limit_text
# Python import's sucks


db = DataBase()

def limit_text(text: str, lenght: int) -> str:
    return text[:lenght - 3] + '...' if len(text) > lenght else text

def MangaOpen(
        manga_info: Favorite,
        source_languages: dict,
        togle_notify: callable,
        page: ft.Page,
        is_index: bool = False,
        cards_row: ft.Row = None,
        mangas_card_notify: callable = None
    ) -> ft.AlertDialog:
    dl: DownloadManager = page.data['dl']
    manga_title = ft.Text(limit_text(manga_info.name, 35), tooltip=manga_info.name)
    next_chapter = ft.ListTile(
        title=ft.Text('...'),
        trailing=ft.IconButton(ft.icons.ARROW_RIGHT_OUTLINED, disabled=True), 
        leading= ft.IconButton(ft.icons.DOWNLOAD_OUTLINED, disabled=True),
        disabled=True
    )
    def read(source, manga: Favorite, chapter: Chapter, chapters: list[Chapter], language: str=None) -> None:
        manga_title.value = limit_text(manga.name, 35)
        status = ft.Text('Buscando as imagens...', weight=ft.FontWeight.W_500)
        media = 'Capítulo' if manga_info.type == 'manga' else 'Episódio'
        title = ft.Text(f'{media} {chapter.number} - {chapter.title}' if chapter.title else f'{media} {chapter.number}', size=20, weight=ft.FontWeight.BOLD)
        row_content = ft.Row([
            ft.ProgressRing(height=140, width=140),
        ], alignment=ft.MainAxisAlignment.CENTER
        )
        page.dialog.content = ft.Container(
            ft.Column([
                ft.Row([
                    ft.Image(manga.cover, height=200, fit=ft.ImageFit.FIT_HEIGHT, border_radius=10),
                    title,
                ]),
                ft.Container(height=5),
                ft.Divider(height=5, color=ft.colors.GREY_700, thickness=2),
                ft.Container(height=5),
                row_content,
                ft.Row([status], expand=True,alignment=ft.MainAxisAlignment.CENTER),
                ft.Text(f'Pressione F4 para sair do {media.lower()}' if manga_info.type == 'manga' else 'O player pode demorar um pouco...', size=15, weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )
        page.update()
        if manga.type == 'manga':
            pages = dl.get_chapter_image_urls(source, chapter.id)
            status.value = 'Baixando as imagens...'
            page.update()
            images_b64 = dl.get_base64_images(pages)
            if not images_b64:
                status.value = 'Erro ao baixar as imagens!'
                status.color = ft.colors.RED_500
                page.update()
                return
            status.value = 'Pronto!'
            page.update()
            page.data['chapter_images'] = images_b64
            page.data['manga_chapters'] = chapters
            page.data['chapter_title'] = f'{chapter.title} - {chapter.number}' if chapter.title else chapter.number
            page.data['manga'] = manga
            page.data['chapter'] = chapter
            page.data['source'] = source
            if language:
                page.data['language'] = language
            page.data['is_index'] = False
            page.data['MangaOpen'] = lambda: MangaOpen(manga_info, source_languages, togle_notify, page, is_index, cards_row, mangas_card_notify)
            if is_index:
                page.data['is_index'] = True
            page.go('/reader')
            return
        if not dl.is_mpv_installed():
            status.value = 'Baixando o player de vídeo...'
            page.update()
            dl.download_mpv()
        status.value = 'Procurando o episódio...'
        page.update()
        episode_urls = dl.get_episode_url(source, chapter.id)
        print(episode_urls)
        if type(episode_urls) == bool:
            status.value = 'Erro ao encontrar o episódio!'
            status.color = ft.colors.RED_500
            row_content.controls = []
            page.update()
            return
        def select_option(ep: Episode):
            row_content.controls = [
                ft.ProgressRing(height=140, width=140),
            ]
            page.update()
            if not db.is_readed(source, manga.id, manga.source_id, chapter.id, language if language else None):
                db.add_readed(source, manga.id, manga.source_id, chapter.id, language if language else None)
            if source == '':
                status.value = 'Baixando o episódio...'
                page.update()
                path = dl.download_episode(chapter.number, manga, ep)
                ep.url = path
            status.value = 'Abrindo o player...'
            page.update()
            dl.start_video_player(ep.url, f'{manga.name} - {chapter.number}', ep.headers, ep.cookies)
            MangaOpen(manga_info, source_languages, togle_notify, page, is_index, cards_row, mangas_card_notify)
            return
        if type(episode_urls) == list:
            status.value = 'Escolha uma opção:'
            row_content.controls = [
                ft.Column([
                    ft.FilledButton(episode.label, on_click=lambda e, ep=episode: select_option(ep), width=200)
                    for episode in episode_urls
                ], height=220, width=140, alignment=ft.MainAxisAlignment.CENTER)
            ]
            page.update()
            return
        status.value = 'Abrindo o player...'
        page.update()
        if not db.is_readed(source, manga.id, manga.source_id, chapter.id, language if language else None):
            db.add_readed(source, manga.id, manga.source_id, chapter.id, language if language else None)
        if source == 'av':
            status.value = 'Baixando o episódio...'
            page.update()
            path = dl.download_episode(chapter.number, manga, episode_urls)
            episode_urls.url = path
        dl.start_video_player(episode_urls.url, f'{manga.name} - {chapter.number}', episode_urls.headers, episode_urls.cookies)
        MangaOpen(manga_info, source_languages, togle_notify, page, is_index, cards_row, mangas_card_notify)

    btns_list: list[ft.IconButton] = []
    def togle_readed(source, manga: Favorite, chapter: Chapter, language: str=None):
        if db.is_readed(source, manga.id, manga.source_id, chapter.id, language if language else None):
            db.delete_all_readed_above(manga, source, chapter, chapters_by_source[f'{source}_{language_options.value}'], language if language else None)
        else:
            db.add_all_readed_below(manga, source, chapter, chapters_by_source[f'{source}_{language_options.value}'], language if language else None)
        each_readed = db.is_each_readed(source, manga.id, manga.source_id, chapters_by_source[f'{source}_{language_options.value}'])
        icon = ft.icons.REMOVE
        for is_read, btn in zip(each_readed, btns_list):
            if is_read:
                icon = ft.icons.CHECK
            if btn.icon != icon:
                btn.icon = icon
        load_next()
        page.update()
    chapter_search = ft.TextField(
        label='Capítulo...' if manga_info.type == 'manga' else 'Episódio...',
        width=240,
        border_radius=20,
        height=40,
        border_color=ft.colors.GREY_700,
        focused_border_color=ft.colors.BLUE_300
    )
    column_chapters = ft.Column(height=8000, width=240, scroll='always')
    options = []
    text = ''
    match manga_info.source:
        case 'md':
            text = 'MangaDex'
        case 'ml':
            text = 'MangaLivre'
        case 'ms':
            text = 'MangaSee'
        case 'mc':
            text = 'MangasChan'
        case 'mf':
            text = 'MangaFire'
        case 'mx':
            text = 'MangaNexus'
        case 'gkk':
            text = 'Gekkou Scans'
        case 'tsct':
            text = 'Taosect Scans'
        case 'tcb':
            text = 'TCB Scans'
        case 'op':
            text = 'OP Scans'
        case 'lmorg':
            text = 'LerManga.org'
        case 'av':
            text = 'AnimesVision'
        case 'af':
            text = 'AnimeFire'
        case 'ao':
            text = 'AnimesOnline'
        case 'ah':
            text = 'AnimesHouse'
        case 'oa':
            text = 'OtakuAnimes'
        case 'go':
            text = 'Goyabu'
        case 'ba':
            text = 'BetterAnime'
    options.append(ft.dropdown.Option(manga_info.source, text))
    if manga_info.source_id in [
        '5/one-piece',
        'One-Piece',
        'one-piece',
        13,
        '13',
        'dkw',
        'a1c7c817-4e59-43b7-9365-09675a149a6f',
    ] and manga_info.type == 'manga':
        options.append(ft.dropdown.Option('opex', 'One Piece Ex'))
    chapters_by_source = {}
    source_options = ft.Dropdown(
        options=options,
        width=140,
        value=manga_info.source
    )
    language_options = ft.Dropdown(
        options=[ft.dropdown.Option(i, i) for i in source_languages[source_options.value]],
        width=140,
        value=source_languages[source_options.value][0]
    )
    if len(source_options.options) == 1:
        source_options.disabled = True
    if len(source_languages[source_options.value]) == 1:
        language_options.disabled = True
    
    def load_next():
        chapters: list[Chapter] = chapters_by_source[f'{manga_info.source}_{language_options.value}']
        each_readed = db.is_each_readed(manga_info.source, manga_info.id, manga_info.source_id, chapters)
        if not chapters:
            next_chapter.title.value = '0 capítulos!'
            next_chapter.trailing.icon = ft.icons.CHECK
            next_chapter.leading.icon = ft.icons.CIRCLE
            next_chapter.on_click = None
            next_chapter.trailing.disabled = True
            next_chapter.leading.disabled = True
        if len(chapters) == 1 and not each_readed[0]:
            next_chapter.disabled = False
            next_chapter.title.value = chapters[0].number if len(str(chapters[0].number)) and chapters[0].number is not None else chapters[0].title
            next_chapter.trailing.icon = ft.icons.ARROW_RIGHT_OUTLINED
            next_chapter.leading.icon = ft.icons.DOWNLOAD_OUTLINED
            next_chapter.on_click = lambda e, source=source_options.value, manga=manga_info, chapter=chapters[0]: read(source, manga, chapter, chapters_by_source[f'{source}_{language_options.value}'], language_options.value if len(source_languages[source_options.value]) > 1 else None)
            next_chapter.trailing.on_click = lambda e, chp=chapters[0]: togle_next(chp)
            next_chapter.leading.on_click = lambda e, source=source_options.value, chapter=chapters[0]: dl.download_chapter(manga_info, source, chapter) if manga_info.type == 'manga' else dl.download_episode(manga_info, source, chapter)
            next_chapter.trailing.disabled = False
            next_chapter.leading.disabled = False
        for i, chapter in enumerate(chapters):
            if i == 0 and each_readed[i]:
                next_chapter.title.value = 'Tudo lido!' if manga_info.type == 'manga' else 'Tudo assistido!'
                next_chapter.trailing.icon = ft.icons.CHECK
                next_chapter.leading.icon = ft.icons.CIRCLE
                next_chapter.on_click = None
                next_chapter.trailing.disabled = True
                next_chapter.leading.disabled = True
                if manga_info.type == 'anime':
                    next_chapter.title.size = 13
                break
            if not each_readed[i] and len(chapters) > 1:
                if chapters[i] == chapters[-1]:                
                    next_chapter.disabled = False
                    next_chapter.title.value = chapter.number if len(str(chapter.number)) and chapter.number is not None else chapter.title
                    next_chapter.trailing.icon = ft.icons.ARROW_RIGHT_OUTLINED
                    next_chapter.leading.icon = ft.icons.DOWNLOAD_OUTLINED
                    next_chapter.on_click = lambda e, source=source_options.value, manga=manga_info, chapter=chapter: read(source, manga, chapter, chapters_by_source[f'{source}_{language_options.value}'], language_options.value if len(source_languages[source_options.value]) > 1 else None)
                    next_chapter.trailing.on_click = lambda e, chp=chapter: togle_next(chp)
                    next_chapter.leading.on_click = lambda e, source=source_options.value, chapter=chapter: dl.download_chapter(manga_info, source, chapter) if manga_info.type == 'manga' else dl.download_episode(manga_info, source, chapter)
                    next_chapter.trailing.disabled = False
                    next_chapter.leading.disabled = False
                    break
                if each_readed[i+1]:
                    next_chapter.disabled = False
                    next_chapter.title.value = chapter.number if len(str(chapter.number)) and chapter.number is not None else chapter.title
                    next_chapter.trailing.icon = ft.icons.ARROW_RIGHT_OUTLINED
                    next_chapter.leading.icon = ft.icons.DOWNLOAD_OUTLINED
                    next_chapter.on_click = lambda e, source=source_options.value, manga=manga_info, chapter=chapter: read(source, manga, chapter, chapters_by_source[f'{source}_{language_options.value}'], language_options.value if len(source_languages[source_options.value]) > 1 else None)
                    next_chapter.trailing.on_click = lambda e, chp=chapter: togle_next(chp)
                    next_chapter.leading.on_click = lambda e, source=source_options.value, chapter=chapter: dl.download_chapter(manga_info, source, chapter) if manga_info.type == 'manga' else dl.download_episode(manga_info, source, chapter)
                    next_chapter.trailing.disabled = False
                    next_chapter.leading.disabled = False
                    break
        page.update()


    def togle_next(chapter: Chapter):
        if db.add_readed(
            source_options.value, 
            manga_info.id, 
            manga_info.source_id if source_options.value != 'opex' else 'opex', 
            chapter.id, language_options.value if len(source_languages[source_options.value]) > 1 else None
            ):
            each_readed = db.is_each_readed(manga_info.source, manga_info.id, manga_info.source_id, chapters_by_source[f'{manga_info.source}_{language_options.value}'])
            icon = ft.icons.REMOVE
            for i, btn in enumerate(btns_list):
                if each_readed[i]:
                    icon = ft.icons.CHECK
                btn.icon = icon
            load_next()
            page.update()

    def load_chapters(query: str=None) -> None:
        btns_list.clear()
        language_options.options = [ft.dropdown.Option(i, i) for i in source_languages[source_options.value]]
        if len(source_languages[source_options.value]) == 1:
            language_options.value = source_languages[source_options.value][0]
            language_options.disabled = True
        source_options.disabled = True
        language_options.disabled = True
        download_all.disabled = True
        download_not_readed.disabled = True
        if not query: chapter_search.disabled = True
        column_chapters.controls = [
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
            if manga_info.type == 'manga':
                chapters = dl.get_chapters(source_options.value, manga_info.source_id if source_options.value != 'opex' else None) if len(source_languages[source_options.value]) == 1 \
                    else dl.get_chapters(source_options.value, manga_info.source_id, language_options.value)
            else:
                chapters = dl.get_episodes(source_options.value, manga_info.source_id if source_options.value != 'opex' else None)
            chapters_by_source[f'{source_options.value}_{language_options.value}'] = chapters
        if type(chapters) == bool:
            column_chapters.controls = [
                ft.ListTile(
                    title=ft.Text(f'Erro ao carregar os {'capítulos' if manga_info.type == 'manga' else 'episódios'}!', color=ft.colors.RED_500),
                )
            ]
            if len(source_languages[source_options.value]) > 1:
                language_options.disabled = False
            if len(source_options.options) > 1:
                source_options.disabled = False
            page.update()
            return
        column_chapters.controls = []
        if not chapters:
            column_chapters.controls = [
                ft.ListTile(
                    title=ft.Text(
                        'Nenhum capítulo encontrado nesse idioma, jovem!' if query == None else f'Nenhum resultado para "{query}"'
                    ),
                )
            ]
            if len(source_languages[source_options.value]) > 1:
                language_options.disabled = False
            if len(source_options.options) > 1:
                source_options.disabled = False
            page.update()
            load_next()
            return
        is_each_readed = db.is_each_readed(
            source_options.value, 
            manga_info.id,
            manga_info.source_id
            if source_options.value != 'opex' else 'opex', 
            chapters
        )
        icon = ft.icons.REMOVE
        for is_read, chapter in zip(is_each_readed, chapters):
            if is_read:
                icon = ft.icons.CHECK
            btn_read = ft.IconButton(icon, on_click=lambda e, source=source_options.value, manga=manga_info, chapter=chapter, language=language_options.value: togle_readed(source, manga, chapter, language if len(source_languages[source_options.value]) > 1 else None))
            btns_list.append(btn_read)
            if query and chapter.number:
                if str(query).lower() not in str(chapter.number).lower():
                    continue
            column_chapters.controls.append(
                ft.ListTile(
                    title=ft.Text(chapter.number if len(str(chapter.number)) and chapter.number is not None else chapter.title, tooltip=chapter.title),
                    trailing=btn_read, 
                    leading= ft.IconButton(ft.icons.DOWNLOAD_OUTLINED, on_click=lambda e, source=source_options.value, chapter=chapter: dl.download_chapter(manga_info, source, chapter) if manga_info.type == 'manga' else dl.download_episode(manga_info, source, chapter)),
                    on_click=lambda e, source=source_options.value, chapter=chapter: read(source, manga_info, chapter, chapters, language_options.value if len(source_languages[source_options.value]) > 1 else None),
                    key=chapter.id
                )
            )
        load_next()
        if len(source_options.options) > 1:
            source_options.disabled = False
        if len(source_languages[source_options.value]) > 1:
            language_options.disabled = False
        download_all.disabled = False if manga_info.type == 'manga' else True
        download_not_readed.disabled = False if manga_info.type == 'manga' else True
        chapter_search.disabled = False
        last_readed = db.get_last_readed(manga_info.id)
        # list_chapters.scroll_to(key=last_readed['chapter_id'] if last_readed else None)
        page.update()
    download_all = ft.ElevatedButton(
        text='Baixar tudo',
        on_click=lambda e: dl.download_all_chapters(manga_info, source_options.value, chapters_by_source[f'{source_options.value}_{language_options.value}']))
    download_not_readed = ft.ElevatedButton(
        text='Baixar não lidos',
    )
    def download_not_readed_chapters(_=None):
        chapters: list[Chapter] = chapters_by_source[f'{source_options.value}_{language_options.value}']
        each_readed = db.is_each_readed(manga_info.source, manga_info.id, manga_info.source_id, chapters)
        chapters_to_download = []
        for is_readed, chapter in zip(each_readed, chapters):
            if is_readed:
                break
            chapters_to_download.append(chapter)
        if chapters_to_download:
            dl.download_all_chapters(
                manga_info, 
                source_options.value, 
                chapters_to_download
            )
    download_not_readed.on_click = download_not_readed_chapters
    
    switch = ft.Switch(
        value=db.is_notify(manga_info.id),
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
        if is_index:
            cards_row.controls = mangas_card_notify(cards_row, page)
        column_chapters.controls = []
        alert.open = False
        page.update()
    alert = ft.AlertDialog(
        title=ft.Row([manga_title, ft.IconButton(ft.icons.CLOSE, on_click=close)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        content=ft.Container(
            ft.Row([
                ft.Column([
                    ft.Container(ft.Image(manga_info.cover, height=250, fit=ft.ImageFit.FIT_HEIGHT, border_radius=10), padding=5),
                    source_options,
                    language_options,
                    switch,
                    download_all,
                    download_not_readed,
                ]),
                ft.Column([
                    ft.Card(next_chapter, width=250),
                    chapter_search,
                    ft.Card(column_chapters, width=250, height=400),
                ])
            ]), height=500, width=430
        ), on_dismiss=close
    )
    page.dialog = alert
    alert.open = True
    page.update()
    load_chapters()
