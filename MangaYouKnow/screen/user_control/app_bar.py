import flet as ft


def NavBar(page: ft.Page) -> ft.NavigationRail:

    NavBar = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=90,
        bgcolor=ft.colors.GREY_900,
        width=90,
        height=1200,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.icons.HOME_OUTLINED,
                selected_icon=ft.icons.HOME_ROUNDED,
                label='Home',
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.BOOKMARK_OUTLINE,
                selected_icon=ft.icons.BOOKMARK_ROUNDED,
                label='Favoritos'
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.SETTINGS_OUTLINED,
                selected_icon=ft.icons.SETTINGS_ROUNDED,
                label='Configs'
            )
        ]
    )

    def change_route(e):
        if e.control.selected_index == 0:
            page.go('/')
        if e.control.selected_index == 1:
            page.go('/favorites')
        if e.control.selected_index == 2:
            page.go('/configs')

    NavBar.on_change = change_route

    return NavBar

    # Code inspiration by CodingJQ
    # https://www.youtube.com/@codingjq
    # https://github.com/codingjq/flet-routing-tutorial/tree/main

