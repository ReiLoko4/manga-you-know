from PIL import Image
from pathlib import Path
from customtkinter import *
from threading import Thread
from myk_db import MangaYouKnowDB
from myk_dl import MangaYouKnowDl
from myk_thread import ThreadManager



__version__ = '0.1b'



class MangaYouKnowGUI:
    def __init__(self):
        set_appearance_mode('System')
        set_default_color_theme('green')
        self.main_w = CTk()
        self.main_w.geometry('770x630+300+40')
        self.main_w.resizable(width=False, height=False)
        self.main_w.wm_title(f'Manga You Know {__version__}')
        # self.main_w.wm_iconbitmap('assets/novoicon')
        self.end = False
        def destroy(window:CTk):
            print('cabo')
            self.end = True
            window.destroy()
        self.main_w.protocol('WM_DELETE_WINDOW', lambda: destroy(self.main_w))
        self.informative_text = CTkTextbox(self.main_w,width=160, height=80)
        self.informative_text.place(x=20, y=20)
        self.informative_text.insert(1.0, 'Todos mangás\nem dia \nmeu consagrado!')
        self.informative_text.configure(state='disabled')
        self.tab_to_read = CTkFrame(self.main_w, width=140, height=510)
        self.tab_to_read.place(x=20, y=109)
        self.sidebar = CTkScrollableFrame(self.tab_to_read, width=140, height=495)
        self.sidebar.pack()
        self.search_entry = CTkEntry(self.main_w, placeholder_text='Nome do mangá (somente favoritos)', width=450)
        self.search_entry.place(x=210, y=20)
        self.search_ico = CTkImage(Image.open('assets/search.ico'))
        self.search_btn = CTkButton(self.main_w, text=None, width=27, image=self.search_ico)
        self.search_btn.place(x=670, y=20)
        self.main_tabs = CTkTabview(self.main_w, width=550, height=566)
        self.main_tabs.pack(anchor=E, padx=12, pady=(50,14))
        self.main_tabs.add('Favoritos')
        self.main_tabs.add('Adicionar')
        self.main_tabs.add('Configurações')
        self.main_tabs.add('Ajuda')
        # self.main_tabs._segmented_button.place(x=0,y=10)
        self.tab_favs = CTkScrollableFrame(self.main_tabs.tab('Favoritos'), width=515, height=20000)
        self.fav_entry = CTkEntry(self.main_tabs.tab('Adicionar'), placeholder_text='https://mangalivre.net/manga/nomeDoManga/idDoManga', width=330)
        self.fav_entry.place(x=50, y=30)
        self.btn_add = CTkButton(self.main_tabs.tab('Adicionar'), text='Pesquisar', width=70, command=self.add_manga)
        self.btn_add.place(x=390, y=30)
        self.tab_config = CTkScrollableFrame(self.main_tabs.tab('Configurações'), width=515, height=20000)
        self.tab_config.pack()
        self.img_edit = CTkImage(Image.open('assets/edit.ico'), size=(15,15))
        self.img_search = CTkImage(Image.open('assets/search.ico'), size=(15,15))
        self.img_trash = CTkImage(Image.open('assets/trash.ico'), size=(15,20))
        self.img_fav = CTkImage(Image.open('assets/fav.ico'), size=(25,25))
        self.connection_data = MangaYouKnowDB()
        self.connection_api = MangaYouKnowDl()

    def run(self):
        new = Thread(target=lambda: self.update_sidebar())
        new.start()
        self.update_tab_favs()
        self.main_w.mainloop()

    def update_tab_favs(self):
        if self.tab_favs.winfo_exists():
            for child in self.tab_favs.winfo_children():
                child.destroy()
        self.tab_favs.pack()
        data = self.connection_data.get_database()
        x = [10, 180, 350]
        self.y = 10
        self.last_x = 0
        offset = 0
        if len(data) != 0:
            card_space = CTkFrame(self.tab_favs, width=160, height=270, fg_color='transparent')
            card_space.pack(pady=10, anchor=W)
            for manga in data:
                card = CTkFrame(self.tab_favs, width=160, height=270)
                card.place(x=x[offset], y=self.y)
                self.last_x = x[offset]
                offset+=1
                if offset == 3 and manga[0] not in data[-1][0]:
                    offset = 0
                    self.y+=290
                    card_space = CTkFrame(self.tab_favs, width=160, height=270, fg_color='transparent')
                    card_space.pack(pady=10, anchor=W)
                capa1 = CTkImage(Image.open(manga[3]), size=(145, 220))
                img1 = CTkLabel(master=card, text='', image=capa1, width=140, height=150)
                img1.place(x=8, y=6)
                button1 = CTkButton(master=card, text='Ver capítulos', width=107, command=lambda id=manga[0]: self.show_manga(id))
                button1.place(x=8, y=235)
                buttonedit1 = CTkButton(master=card, text=None, width=15, image=self.img_edit, fg_color='white', command=lambda id=manga[0]: print(id))
                buttonedit1.place(x=123, y=235)

    def update_sidebar(self):
        database = self.connection_data.get_database()
        threads = ThreadManager()
        for data in database:
            t = Thread(target=lambda data=data: each_card(self, data))
            threads.add_thread(t)
            def each_card(self:MangaYouKnowGUI, data:list):
                chapters = self.connection_api.get_manga_chapters(data[0], data[3].split('/')[-3] if '/' in data[3] else data[3].split('\\')[-3])
                chapters_to_read = []
                for chapter in chapters:
                    if chapter[0] == data[2]: break
                    chapters_to_read.append(chapter)
                if len(chapters_to_read) == 0: return False
                if self.end: return False
                card = CTkFrame(self.sidebar, width=130, height=50, fg_color='transparent')
                card.pack(padx=10, pady=5)
                btn_title = CTkButton(card, width=120, height=30, text=(data[1])[:16], )
                btn_title.pack()
                chapters_frame = CTkFrame(card, width=80, height=30, border_width=1)
                chapters_frame.pack()
                remaing_chapters = CTkLabel(chapters_frame, width=80, height=30, text=f'+{len(chapters_to_read)}')
                remaing_chapters.pack(padx=2, pady=(0,2))
        threads.start()

    def frame_change(self, frame:CTkFrame):
        if frame.winfo_exists(): frame.destroy()
        else: frame.pack()

    def add_manga(self):
        try:
            manga_name = self.fav_entry.get().split('/')[-2]
            manga_id = self.fav_entry.get().split('/')[-1]
        except:
            return False
        manga_info = self.connection_api.download_manga_cover(manga_name, manga_id)
        if not manga_info: return False
        tab_add = CTkToplevel()
        tab_add.geometry('390x310+500+150')
        tab_add.resizable(False, False)
        tab_add.wm_title('Pesquisar')
        def destroy(window:CTkToplevel):
            window.destroy()
            self.main_w.grab_set()
        tab_add.protocol('WM_DELETE_WINDOW', lambda: destroy(tab_add))
        img = CTkImage(Image.open(manga_info[0]), size=(172, 272.25))
        frame = CTkFrame(tab_add, width=390, height=310)
        frame.pack(padx=10, pady=10)
        img_label = CTkLabel(frame, width=145, height=220, image=img,text=None)
        img_label.place(x=10, y=10)
        font_text = CTkFont('Times new Roman', size=20)
        manga_title = CTkTextbox(frame, width=175, height=100, font=font_text)
        manga_title.place(x=190, y=10)
        manga_title.insert(1.0, f'\n{manga_info[1]}')
        manga_title.configure(state='disabled')
        manga_chapters = CTkTextbox(frame, width=175, height=30)
        manga_chapters.place(x=190, y=120)
        manga_chapters.insert(1.0, 'Buscando capítulos...')
        manga_chapters.configure(state='disabled')
        text_fav = CTkTextbox(frame, width=100, height=33) 
        text_fav.place(x=215, y=250)
        text_fav.insert(1.0, '      Favoritar')
        text_fav.configure(state='disabled')
        def favorite(self:MangaYouKnowGUI):
            if self.connection_data.add_manga([manga_id, manga_info[1], '', manga_info[0]]): 
                tab_add.destroy()
                self.main_w.grab_set()
            else:
                text_fav.configure(state='normal')
                text_fav.delete(1.0, END)
                text_fav.insert(1.0, 'O mangá já foi favoritado!')
                text_fav.configure(state='disabled')
                return False
            chapters = self.connection_data.get_database()
            card = CTkFrame(self.tab_favs, width=160, height=270)
            if self.last_x in [0, 350]:
                card_space = CTkFrame(self.tab_favs, width=160, height=270, fg_color='transparent')
                card_space.pack(pady=10, anchor=W)
                if self.last_x == 350: self.y += 290
                self.last_x = 10
                card.place(x=10, y=self.y)
            else:
                self.last_x += 170 
                card.place(x=self.last_x, y=self.y)
            capa = CTkImage(Image.open(chapters[-1][3]), size=(145, 220))
            img = CTkLabel(card, text='', image=capa, width=140, height=150)
            img.place(x=8, y=6)
            button = CTkButton(card, text='Ver capítulos', width=107, command=lambda id=chapters[-1][0]: self.show_manga(id))
            button.place(x=8, y=235)
            button_edit = CTkButton(card, text=None, width=15, image=self.img_edit, fg_color='white', command=lambda id=chapters[-1][0]: print(id))
            button_edit.place(x=123, y=235)
        button_fav = CTkButton(frame, width=30, height=30, text=None, image=self.img_fav, command=lambda: favorite(self))
        button_fav.place(x=320, y=250)
        tab_add.grab_set()
        def search_chapters(self:MangaYouKnowGUI, manga_id:str, manga_name:str):
            chapters = self.connection_api.get_manga_chapters(manga_id, manga_name)
            if not tab_add.winfo_exists(): return False
            manga_chapters.configure(state='normal')
            manga_chapters.delete(1.0, END)
            manga_chapters.insert(END, f'{len(chapters)} capítulos disponíveis')
            manga_chapters.configure(state='disabled')
            self.connection_data.add_data_chapters(manga_name, chapters)
        chapters_search = Thread(target=lambda: search_chapters(self, manga_id, manga_name))
        chapters_search.start()
        
    def show_manga(self, manga_id:str):
        manga = self.connection_data.get_manga(manga_id)
        window_show = CTkToplevel(self.main_w)
        window_show.geometry('390x440+500+150')
        window_show.resizable(False, False)
        window_show.wm_title(manga[1])
        frame = CTkFrame(window_show, width=390, height=470)
        frame.pack(padx=10, pady=10)
        img = CTkImage(Image.open(manga[3]), size=(172, 272.25))
        img_label = CTkLabel(frame, text=None, image=img)
        img_label.place(x=10,y=10)
        # chapters = CTkScrollableFrame(frame, width=140)
        # chapters.place(x=200, y=10)
        def edit_last_read(chapter):
            self.connection_data.edit_manga(manga_id, chapter)
        list_chapters = self.connection_data.get_data_chapters(manga[3].split('/')[-3] if '/' in manga[3] else manga[3].split('\\')[-3])
        chapters = CTkOptionMenu(frame, values=[i[0] for i in list_chapters], command=edit_last_read)
        chapters.place(x=200, y=10)
        window_show.grab_set()
        

    class Reader:
        def __init__(self, chapter_path:Path) -> None:
            self.chapter_path = chapter_path

        def open(self, chapter_path:Path, type_reader:str):
            pass

        def horizontal(self):
            pass



gui = MangaYouKnowGUI()
gui.run()
