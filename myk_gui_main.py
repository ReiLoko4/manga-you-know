from customtkinter import *
from PIL import Image
from threading import Thread
from myk_db import MangaYouKnowDB
from myk_dl import MangaYouKnowDl


__version__ = '0.1 (BETA)'


class MangaYouKnowGUI:
    def __init__(self):
        set_appearance_mode('System')
        set_default_color_theme('blue')
        self.main_w = CTk()
        self.main_w.geometry('770x630+300+40')
        self.main_w.resizable(width=False, height=False)
        self.main_w.wm_title(f'Manga You Know {__version__}')
        # self.main_w.wm_iconbitmap('assets/novoicon')
        def destroy(window:CTk):
            print('cabo')
            window.destroy()
        self.main_w.protocol('WM_DELETE_WINDOW', lambda: destroy(self.main_w))
        self.tab_informative = CTkFrame(self.main_w, width=160, height=80, bg_color='transparent')
        self.tab_informative.place(x=20, y=20)
        self.informative_text = CTkButton(self.tab_informative,width=160, height=80, text='Todos mangás\n em dia \nmeu consagrado!', state=False, hover=None, fg_color='black')
        self.informative_text.pack()
        self.tab_to_read = CTkFrame(self.main_w, width=140, height=510)
        self.tab_to_read.place(x=20, y=109)
        self.sidebar = CTkScrollableFrame(self.tab_to_read, width=140, height=495)
        self.sidebar.pack()
        self.search_entry = CTkEntry(self.main_w, placeholder_text='Nome do mangá', width=450)
        self.search_entry.place(x=210, y=20)
        self.search_ico = CTkImage(Image.open('assets/search.ico'))
        self.search_btn = CTkButton(self.main_w, text=None, width=27, image=self.search_ico)
        self.search_btn.place(x=670, y=20)
        self.main_tabs = CTkTabview(self.main_w, width=550, height=566)
        self.main_tabs.pack(anchor=E, padx=12, pady=(50,14))
        self.main_tabs.add('Favoritos')
        self.main_tabs.add('Adicionar')
        self.main_tabs.add('Configurações')
        # self.main_tabs._segmented_button.place(x=0,y=10)
        self.tab_favs = CTkScrollableFrame(self.main_tabs.tab('Favoritos'), width=515, height=20000)
        self.tab_favs.pack()
        self.fav_entry = CTkEntry(self.main_tabs.tab('Adicionar'), placeholder_text='https://mangalivre.net/manga/nomeDoManga/idDoManga', width=330)
        self.fav_entry.place(x=50, y=30)
        self.btn_add = CTkButton(self.main_tabs.tab('Adicionar'), text='Pesquisar', width=70, command=self.add_manga)
        self.btn_add.place(x=390, y=30)
        self.tab_config = CTkScrollableFrame(self.main_tabs.tab('Configurações'), width=515, height=20000)
        self.tab_config.pack()
        self.img_edit = CTkImage(Image.open('assets/edit.ico'), size=(15,15))
        self.img_search = CTkImage(Image.open('assets/search.ico'), size=(15,15))
        self.img_trash = CTkImage(Image.open('assets/trash.ico'), size=(15,20))
        self.connection_data = MangaYouKnowDB()
        self.connection_api = MangaYouKnowDl()

    def run(self):
        new = Thread(target=self.update_sidebar)
        new.start()
        self.update_tab_favs()
        self.main_w.mainloop()
        

    def update_tab_favs(self):
        data = self.connection_data.get_database()
        x = [10, 180, 355]
        y = 10
        offset = 0
        if len(data) != 0:
            card_space = CTkFrame(self.tab_favs, width=160, height=270, fg_color='transparent')
            card_space.pack(pady=10, anchor=W)
            for manga in data:
                card = CTkFrame(self.tab_favs, width=160, height=270)
                card.place(x=x[offset], y=y)
                offset+=1
                if offset == 3:
                    offset = 0
                    y+=290
                    card_space = CTkFrame(self.tab_favs, width=160, height=270, fg_color='transparent')
                    card_space.pack(pady=10, anchor=W) 
                capa1 = CTkImage(Image.open(manga[3]), size=(145, 220))
                img1 = CTkLabel(master=card, text='', image=capa1, width=140, height=150)
                img1.place(x=8, y=6)
                button1 = CTkButton(master=card, text='Ver capítulos', width=107)
                button1.place(x=8, y=235)
                buttonedit1 = CTkButton(master=card, text=None, width=15, image=self.img_edit, fg_color='white', command=lambda id=manga[0]: print(id))
                buttonedit1.place(x=123, y=235)

    def update_sidebar(self):
        data = self.connection_data.get_database()
        for i in range(len(data)):
            chapters = self.connection_api.get_manga_chapters(data[i][0], data[i][1])
            chapters_to_read = []
            for chapter in chapters:
                if chapter == data[i][2]: break
                chapters_to_read.append(chapter)
            if len(chapters_to_read) == 0: continue
            card = CTkFrame(master=self.sidebar, width=130, height=50, fg_color='transparent')
            card.pack(padx=10, pady=5)
            btn_title = CTkButton(card, width=120, height=30, text=(data[i][1])[:16], )
            btn_title.pack()
            chapters_frame = CTkFrame(card, width=80, height=30, border_width=1)
            chapters_frame.pack()
            remaing_chapters = CTkLabel(chapters_frame, width=80, height=30, text=f'+{len(chapters_to_read)}')
            remaing_chapters.pack(padx=2, pady=(0,2))

    def frame_change(self, frame:CTkFrame):
        if frame.winfo_exists(): frame.destroy()
        else: frame.pack()

    def add_manga(self):
        if not self.fav_entry.get():
            return print(False)
        manga_info = self.connection_api.download_manga_cover(self.fav_entry.get().split('/')[-2], self.fav_entry.get().split('/')[-1])
        tab_add = CTkToplevel(self.main_w)
        tab_add.geometry('370x450+500+150')
        tab_add.resizable(width=False, height=False)
        tab_add.wm_title('Pesquisar')
        img = CTkImage(Image.open(manga_info[0]), size=(172, 272.25))
        img_frame = CTkFrame(tab_add, width=160, height=300)
        img_frame.pack(anchor=W, padx=10, pady=10)
        img_label = CTkLabel(img_frame, width=145, height=220, image=img,text=None)
        img_label.pack()
        manga_name_frame = CTkFrame(tab_add, width=180, height=100)
        manga_name_frame.place(x=190, y=10)
        manga_name = CTkLabel(manga_name_frame, width=180, height=100, text=manga_info[1])
        manga_name.pack()
        tab_add.grab_set()
        



gui = MangaYouKnowGUI()
gui.run()