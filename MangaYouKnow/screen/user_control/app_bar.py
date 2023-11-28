import flet as ft


def NavBar(page: ft.Page) -> ft.NavigationRail:

    NavBar = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.SELECTED,
        min_width=90,
        width=90,
        height=1200,
        bgcolor=ft.colors.GREY_900,
        group_alignment=-0.9,
        animate_size=300,
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
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.CONTACTS_OUTLINED,
                selected_icon=ft.icons.CONTACTS_ROUNDED,
                label='About'
            )
        ]
    )
    routes = {
        0: '/',
        1: '/favorites',
        2: '/configs',
        3: '/about'
    }
    NavBar.on_change = lambda e: page.go(routes[e.control.selected_index])
    return NavBar

    # Code inspiration by CodingJQ
    # https://www.youtube.com/@codingjq
    # https://github.com/codingjq/flet-routing-tutorial/tree/main

