from customtkinter import *
from PIL import Image
from threading import Thread
from myk_db import MangaYouKnowDB
from myk_dl import MangaYouKnowDl



class MangaYouKnowGUI:
    def __init__(self):
        set_appearance_mode('System')
        set_default_color_theme('blue')
        self.main_w = CTk()
        self.main_w.geometry('770x630+300+80')
        self.main_w.resizable(width=False, height=False)
        self.main_w.wm_title('Manga You Know')
        # self.main_w.wm_iconbitmap('assets/novoicon')
        self.tab_to_read = CTkFrame(self.main_w, width=140, height=600)
        self.tab_to_read.place(x=20, y=20)
        self.sidebar = CTkScrollableFrame(self.tab_to_read, width=140, height=585)
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
        self.tab_favs = CTkScrollableFrame(self.main_tabs.tab('Favoritos'), width=515, height=20000)
        self.tab_favs.pack()
        self.entry_new_fav = CTkEntry(self.main_tabs.tab('Adicionar'), placeholder_text='https://mangalivre.net/genero/nomeDoManga/idDoManga', width=330)
        self.entry_new_fav.place(x=50, y=30)
        btn_add = CTkButton(self.main_tabs.tab('Adicionar'), text='Adicionar', width=70, command=self.add_manga)
        btn_add.place(x=390, y=30)
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
        y = 10
        x = [10, 180, 355]
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
                capa1 = CTkImage(Image.open(manga[4]), size=(145, 220))
                img1 = CTkLabel(master=card, text='', image=capa1, width=140, height=150)
                img1.place(x=8, y=6)
                button1 = CTkButton(master=card, text='Ver capítulos', width=107)
                button1.place(x=8, y=235)
                buttonedit1 = CTkButton(master=card, text=None, width=15, image=self.img_edit, fg_color='white', command=lambda id=manga[0]: print(id))
                buttonedit1.place(x=123, y=235)

    def update_sidebar(self):
        data = self.connection_data.get_database()
        for i in range(len(data)):
            chapters = self.connection_api.get_manga_chapters(data[i][0])
            chapters_to_read = []
            for chapter in chapters:
                if chapter == data[i][2]: break
                chapters_to_read.append(chapter)
            if len(chapters_to_read) == 0: continue
            card = CTkFrame(master=self.sidebar, width=130, height=50, fg_color='transparent')
            card.pack(padx=10, pady=5)
            btn_title = CTkButton(card, width=120, height=30, text=data[i][1])
            btn_title.pack()
            chapters_frame = CTkFrame(card, width=80, height=len(chapters_to_read) * 30)
            chapters_frame.pack()
            for chapter in chapters_to_read:
                text = CTkLabel(chapters_frame, width=80, height=30, text=chapter)
                text.pack(padx=5)

    def frame_change(self, frame:CTkFrame):
        if frame.winfo_exists(): frame.destroy()
        else: frame.pack()

    def add_manga(self):
        pass



gui = MangaYouKnowGUI()
gui.run()