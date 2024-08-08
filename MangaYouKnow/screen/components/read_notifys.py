import flet as ft
from backend.managers import DownloadManager



def ReadNotifys(page: ft.Page):
    dl: DownloadManager = page.data['dl']