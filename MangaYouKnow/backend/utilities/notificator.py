from win10toast import ToastNotifier
from pathlib import Path
import requests


class Notificator:
    def __init__(self):
        self.notify = ToastNotifier()
        self.img_url = 'https://github.com/ReiLoko4/manga-you-know/assets/103978193/7f88ff21-dc8e-44b2-8eea-5bde6e5d074c'
        self.img_path = Path('database/app.ico')

    def show(self, title: str, message: str):
        if not self.img_path.exists():
            self.img_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.img_path, 'wb') as f:
                f.write(requests.get(self.img_url).content)
        self.notify.show_toast(title, message, icon_path=self.img_path, threaded=True)
    