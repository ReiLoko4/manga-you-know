from flet import Image, ImageFit

from screen.constants import LOADING_B64_GIF

def ErrorGif(height = 250, width = 170) -> Image:
    return Image(
        src='https://static-00.iconduck.com/assets.00/error-icon-512x512-mmajyv8q.png',
        width=width,
        height=height,
        fit=ImageFit.FIT_HEIGHT,
      )