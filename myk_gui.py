from PIL import Image
from time import sleep
from pathlib import Path
from customtkinter import *
from threading import Thread
from myk_db import MangaYouKnowDB
from myk_dl import MangaYouKnowDl
from myk_thread import ThreadManager



__version__ = '0.2b'



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
            self.end = True
            window.destroy()
        self.main_w.protocol('WM_DELETE_WINDOW', lambda: destroy(self.main_w))
        self.informative_text = CTkTextbox(self.main_w, width=160, height=80)
        self.informative_text.place(x=20, y=20)
        self.informative_text.insert(1.0, 'Todos mangás\nem dia \nmeu consagrado!')
        self.informative_text.configure(state='disabled')
        self.tab_to_read = CTkFrame(self.main_w, width=140, height=400)
        self.tab_to_read.place(x=20, y=109)
        self.sidebar = CTkScrollableFrame(self.tab_to_read, width=140, height=400)
        self.sidebar.pack()
        self.reload_btn = CTkButton(self.main_w, width=160, height=80, text=None, command=lambda: Thread(target=lambda: self.update_sidebar(True)).start(), image=CTkImage(Image.open('assets/reload.ico'), size=(40, 40)))
        self.reload_btn.place(x=20, y=531)
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
        self.tab_favs = CTkScrollableFrame(self.main_tabs.tab('Favoritos'), width=515, height=600)
        self.fav_entry = CTkEntry(self.main_tabs.tab('Adicionar'), placeholder_text='https://mangalivre.net/manga/nomeDoManga/idDoManga', width=330)
        self.fav_entry.place(x=50, y=30)
        self.btn_add = CTkButton(self.main_tabs.tab('Adicionar'), text='Pesquisar', width=70, command=self.add_manga)
        self.btn_add.place(x=390, y=30)
        self.tab_config = CTkScrollableFrame(self.main_tabs.tab('Configurações'), width=515, height=20000)
        self.tab_config.pack()
        self.frame_welcome = {}
        self.img_edit = CTkImage(Image.open('assets/edit.ico'), size=(15,15))
        self.img_search = CTkImage(Image.open('assets/search.ico'), size=(15,15))
        self.img_trash = CTkImage(Image.open('assets/trash.ico'), size=(15,20))
        self.img_fav = CTkImage(Image.open('assets/fav.ico'), size=(25,25))
        self.connection_data = MangaYouKnowDB()
        self.connection_api = MangaYouKnowDl()

    def run(self):
        self.update_tab_favs()
        Thread(target=lambda: self.update_sidebar()).start()
        self.main_w.mainloop()

    def update_tab_favs(self, delete:bool=False):
        if delete: 
            for children in self.tab_favs.winfo_children():
                children.destroy()
        self.tab_favs.pack()
        if self.frame_welcome.get('welcome') != None: self.frame_welcome['welcome'].destroy()
        self.frame_welcome = {}
        data = self.connection_data.get_database()
        x = [10, 180, 350]
        self.y = 10
        self.last_x = 0
        offset = 0
        if len(data) == 0:
            card_welcome = CTkFrame(self.tab_favs, width=495)
            card_welcome.pack(padx=10, pady=10, anchor=N)
            self.frame_welcome['welcome'] = card_welcome
            text_welcome = CTkTextbox(card_welcome, width=380, height=180, font=('Times new Roman', 16))
            text_welcome.place(x=10,y=10)
            text_welcome.configure(state='disabled')
            btn_welcome = CTkButton(card_welcome,width=80, height=180, text='Leve me lá!', command=lambda: self.main_tabs.set('Adicionar'))
            btn_welcome.place(x=405,y=10)
            def print_text():
                text = ['Seja bem vindo ao MangaYouKnow!', 'Atualmente você não possui nenhum manga favoritado...', 'Se desejar favoritar um manga, escolha entre as opções na \naba #Adicionar', 'Ou copie e cole o link da página do manga na url: \nhttps://mangalivre.net :)']
                for phrase in text:
                    for char in phrase:
                        if self.end: return False
                        if not card_welcome.winfo_exists(): return False
                        text_welcome.configure(state='normal')
                        text_welcome.insert(END, char)
                        text_welcome.configure(state='disabled')
                        sleep(0.07)
                    if self.end: return False
                    if not card_welcome.winfo_exists(): return False
                    text_welcome.configure(state='normal')
                    text_welcome.insert(END, '\n')
                    text_welcome.configure(state='disabled')
                    sleep(0.8)
            Thread(target=print_text).start()
            return False
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
                card_space.pack(pady=10, anchor=W)
            capa = CTkImage(Image.open(manga[3]), size=(145, 220))
            img = CTkLabel(master=card, text='', image=capa, width=140, height=150)
            img.place(x=8, y=6)
            btn_show = CTkButton(master=card, text='Ver capítulos', width=107, command=lambda id=manga[0]: self.show_manga(id))
            btn_show.place(x=8, y=235)
            btn_edit = CTkButton(master=card, text=None, width=15, image=self.img_edit, fg_color='white', command=lambda id=manga[0]: self.edit_manga(id))
            btn_edit.place(x=123, y=235)
                
    def update_sidebar(self, delete:bool=False):
        self.reload_btn.configure(state='disabled')
        if delete:
            for card in self.cards_sidebar_destroy:
                card.destroy()
        global mangas_to_read
        mangas_to_read = 0
        self.cards_sidebar_destroy = []
        self.cards_sidebar = {}
        database = self.connection_data.get_database()
        threads = ThreadManager()
        for data in database:
            t = Thread(target=lambda data=data: each_card(data))
            threads.add_thread(t)
            def each_card(data:list):
                chapters = self.connection_api.get_manga_chapters(data[0], data[4])
                chapters_to_read = []
                for chapter in chapters:
                    if chapter[0] == data[2]: break
                    chapters_to_read.append(chapter)
                if len(chapters_to_read) == 0: return False
                if self.end: return False
                if not self.connection_data.get_manga(data[0]): return False
                global mangas_to_read
                mangas_to_read += 1
                self.informative_text.configure(state='normal')
                self.informative_text.delete(1.0, END)
                self.informative_text.insert(1.0, f'Você tem um total de {mangas_to_read} \nmanga(s) para ler!')
                self.informative_text.configure(state='disabled')
                card = CTkFrame(self.sidebar, width=130, height=50, fg_color='transparent')
                card.pack(padx=10, pady=5)
                self.cards_sidebar_destroy.append(card)
                self.cards_sidebar[data[0]] = card
                btn_title = CTkButton(card, width=120, height=30, text=(data[1])[:16], command=lambda id=data[0]: self.show_manga(id))
                btn_title.pack()
                self.cards_sidebar[f'{data[0]} title'] = btn_title
                chapters_frame = CTkFrame(card, width=80, height=30, border_width=1)
                chapters_frame.pack()
                remaing_chapters = CTkLabel(chapters_frame, width=80, height=30, text=f'+{len(chapters_to_read)}')
                remaing_chapters.pack(padx=2, pady=(0,2))
                self.cards_sidebar[f'{data[0]} chapters'] = remaing_chapters
        threads.start()
        threads.join()
        self.reload_btn.configure(state='normal')

    def frame_change(self, frame:CTkFrame):
        if frame.winfo_exists(): frame.destroy()
        else: frame.pack()

    def add_manga(self):
        try:
            manga_name = self.fav_entry.get().split('/')[-2]
            manga_id = self.fav_entry.get().split('/')[-1]
        except:
            return False
        if not str(manga_id).isdigit():
            for char in manga_id:
                if not char.isdigit(): manga_id = manga_id.replace(char, '')
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
        def favorite():
            if self.connection_data.add_manga([manga_id, manga_info[1], '', manga_info[0], manga_name]): 
                tab_add.destroy()
                self.fav_entry.delete(0, END)
                self.main_w.grab_set()
            else:
                text_fav.configure(state='normal')
                text_fav.delete(1.0, END)
                text_fav.insert(1.0, 'O mangá já foi favoritado!')
                text_fav.configure(state='disabled')
                return False
            self.update_tab_favs()
        button_fav = CTkButton(frame, width=30, height=30, text=None, image=self.img_fav, command=lambda: favorite())
        button_fav.place(x=320, y=250)
        tab_add.grab_set()
        def search_chapters():
            chapters = self.connection_api.get_manga_chapters(manga_id, manga_name)
            if not tab_add.winfo_exists(): return False
            manga_chapters.configure(state='normal')
            manga_chapters.delete(1.0, END)
            manga_chapters.insert(END, f'{len(chapters)} capítulos disponíveis')
            manga_chapters.configure(state='disabled')
            self.connection_data.add_data_chapters(manga_name, chapters)
        chapters_search = Thread(target=lambda: search_chapters())
        chapters_search.start()
        
    def show_manga(self, manga_id:str):
        manga = self.connection_data.get_manga(manga_id)
        window_show = CTkToplevel()
        window_show.geometry('390x440+500+150')
        window_show.resizable(False, False)
        window_show.wm_title(manga[1])
        def destroy(window:CTk):
            while True:
                try: window.destroy()
                except: continue
                break
        window_show.protocol('WM_DELETE_WINDOW', lambda: destroy(window_show))
        frame = CTkFrame(window_show, width=390, height=470)
        frame.pack(padx=10, pady=10)
        img = CTkImage(Image.open(manga[3]), size=(129, 204.1875))
        img_label = CTkLabel(frame, text=None, image=img)
        img_label.place(x=20,y=20)
        window_show.grab_set()
        tab_chapters = CTkTabview(frame, width=160, height=240)
        tab_chapters.place(x=170, y=70)
        def load_chapters():
            chapters = self.connection_data.get_data_chapters(manga[4])
            if len(chapters) > 700 and len(chapters) < 1400: cpt_per_frame = 200
            elif len(chapters) > 1400: cpt_per_frame = 600
            else: cpt_per_frame = 100
            tab_chapters.add('1')
            scroll_chapters = CTkScrollableFrame(tab_chapters.tab('1'), width=160, height=240)
            scroll_chapters.pack()
            offset = 1
            num_chapter = 0
            for chapter in chapters:
                if self.end: return False
                if not window_show.winfo_exists(): return False
                try: frame_chapter = CTkFrame(scroll_chapters, width=150, height=30, fg_color='gray')
                except: return False
                frame_chapter.pack(padx=5, pady=3)
                text = CTkLabel(frame_chapter, text=chapter[0])
                text.place(x=5, y=1)
                btn_set_read = CTkButton(frame_chapter, width=40, text=None, image=self.img_edit)
                btn_set_read.place(x=70, y=1)
                num_chapter += 1
                if num_chapter == cpt_per_frame:
                    offset += 1
                    sleep(0.01)
                    tab_chapters.add(str(offset))
                    scroll_chapters = CTkScrollableFrame(tab_chapters.tab(str(offset)), width=160, height=240)
                    scroll_chapters.pack()
                    num_chapter = 0
        Thread(target=load_chapters).start()
        # chapters = CTkScrollableFrame(frame, width=140)
        # chapters.place(x=200, y=10)
        def edit_last_read(chapter):
            if chapter == 'Nenhum lido': chapter = ''
            self.connection_data.set_manga(manga_id, 2, chapter)
        # list_chapters = self.connection_data.get_data_chapters(manga[4])
        # list_chapters.insert(0, 'Nenhum lido')
        # chapters = CTkOptionMenu(frame, values=[i[0] for i in list_chapters], command=edit_last_read)
        # chapters.set('Nenhum lido' if manga[2] == '' else manga[2])
        # chapters.place(x=200, y=10)
        
    def edit_manga(self, manga_id:str):
        manga = self.connection_data.get_manga(manga_id)
        window_edit = CTkToplevel()
        window_edit.geometry('360x390+500+150')
        window_edit.resizable(False, False)
        window_edit.wm_title(manga[1])
        frame = CTkFrame(window_edit, width=340, height=370)
        frame.pack(padx=10, pady=10)
        entry = CTkEntry(frame, width=230, height=34)
        entry.place(x=20, y=20)
        entry.insert(0, manga[1])
        entry.configure(state='disabled')
        def edit_name():
            if entry._state == 'disabled':
                btn_edit.configure(text='Salvar')
                entry.configure(state='normal')
            else:
                btn_edit.configure(text='Editar')
                if len(entry.get()) != 0:
                    self.connection_data.set_manga(manga[0], 1, entry.get())
                    window_edit.wm_title(entry.get())
                    self.cards_sidebar[f'{manga[0]} title'].configure(text=entry.get())
                else: entry.insert(0, manga[1])
                entry.configure(state='disabled')
        btn_edit = CTkButton(frame, width=65, text='Editar', command=edit_name)
        btn_edit.place(x=255, y=23)
        cover = CTkImage(Image.open(manga[3]), size=(172, 272.25))
        label = CTkLabel(frame, text=None, image=cover)
        label.place(x=20,y=80)
        frame_btn = CTkFrame(frame, width=120, height=273)
        frame_btn.place(x=202, y=80)
        def select_folder():
            folder_path = filedialog.askopenfile(filetypes=[
                ('JPEG', '*.jpg;*.jpeg'),
                ('PNG', '*.png'),
                ('GIF', '*.gif'),
                ('BMP', '*.bmp'),
                ('TIFF', '*.tif;*.tiff'),
                ('AVIF', '*.avif'),
                ('WEBP', '*.webp')
            ])
            try:
                label.configure(image=CTkImage(Image.open(folder_path.name), size=(172, 272.25)))
                self.connection_data.set_manga(manga[0], 3, folder_path.name)
                self.update_tab_favs(True)
            except: print('nada selecionado')
        select_button = CTkButton(frame_btn, width=100, text='Selecionar', command=select_folder)
        select_button.place(x=10, y=10)
        text_select_cover = CTkTextbox(frame_btn, width=100, height=80)
        text_select_cover.place(x=10, y=50)
        text_select_cover.insert(0.0, 'Selecione uma\nimagem para\nsubstituir\na capa')
        text_select_cover.configure(state='disabled')
        text_delete = CTkTextbox(frame_btn, width=60, height=30, fg_color='#fa4343')
        text_delete.place(x=10, y=233)
        text_delete.insert(0.0, 'Deletar')
        text_delete.configure(state='disabled')
        def delete():
            window_sure = CTkToplevel()
            window_sure.geometry('300x100+500+300')
            window_sure.resizable(False, False)
            window_sure.wm_title('Tem certeza?')
            frame = CTkFrame(window_sure, width=280, height=80)
            frame.pack(padx=10,pady=10)
            def dell():
                self.connection_data.delete_manga(manga_id)
                window_sure.destroy()
                window_edit.destroy()
                if self.cards_sidebar.get(manga_id) != None: self.cards_sidebar[manga_id].destroy()
                self.update_tab_favs(True)
            btn_ok = CTkButton(frame, text='Sim, deletar', fg_color='#bd110b', hover_color='#fa4343', command=dell)
            btn_ok.place(x=20,y=25)
            btn_cancel = CTkButton(frame,width=80, text='Cancelar', fg_color='gray', hover_color='#c2b3b2', command=lambda: window_sure.destroy())
            btn_cancel.place(x=180,y=25)
            window_sure.grab_set()
        btn_dell = CTkButton(frame_btn, width=25, height=25, image=self.img_trash, text=None, command=delete, fg_color='#bd110b', hover_color='#fa4343')
        btn_dell.place(x=80, y=234)
        window_edit.grab_set()


    class Reader:
        def __init__(self, chapter_path:Path) -> None:
            self.chapter_path = chapter_path

        def open(self, chapter_path:Path):
            pass

        def horizontal(self):
            pass



gui = MangaYouKnowGUI()
gui.run()
