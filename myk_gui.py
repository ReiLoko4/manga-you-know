from PIL import Image
from time import sleep
from pathlib import Path
from customtkinter import *
from threading import Thread
from myk_db import MangaYouKnowDB
from myk_dl import MangaYouKnowDl
from myk_thread import ThreadManager



__version__ = '0.8b'



class MangaYouKnowGUI:
    def __init__(self):
        set_appearance_mode('dark')
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
        self.reload_btn = CTkButton(self.main_w, width=160, height=80, text=None, command=lambda: Thread(target=self.update_sidebar).start(), image=CTkImage(Image.open('assets/reload.ico'), size=(50, 50)))
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
        self.error = 0
        self.mangas_to_read = 0
        self.frame_welcome = {}
        self.cards_sidebar_destroy = {}
        self.img_view = CTkImage(Image.open('assets/view.ico'), size=(15,15))
        self.img_not_view = CTkImage(Image.open('assets/not_view.ico'), size=(15,15))
        self.img_edit = CTkImage(Image.open('assets/edit.ico'), size=(15,15))
        self.img_search = CTkImage(Image.open('assets/search.ico'), size=(15,15))
        self.img_read = CTkImage(Image.open('assets/read.ico'), size=(15,15))
        self.img_file = CTkImage(Image.open('assets/file.ico'), size=(15,15))
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
                
    def update_sidebar(self):
        self.reload_btn.configure(state='disabled')
        self.error = 0
        self.mangas_to_read = 0
        self.cards_sidebar = {}
        database = self.connection_data.get_database()
        threads = ThreadManager()
        for data in database:
            t = Thread(target=lambda data=data: each_card(data))
            threads.add_thread(t)
            def each_card(data:list):
                try:
                    chapters = self.connection_api.get_manga_chapters(data[0], data[4])
                    chapters_to_read = []
                    data = self.connection_data.get_manga(data[0])
                    if not data: return False
                    for chapter in chapters:
                        if chapter[0] == data[2]: break
                        chapters_to_read.append(chapter)
                    if len(chapters_to_read) == 0: return False
                    if self.end: return False
                    text_error = f'Erros: {self.error}' if self.error != 0 else ''
                    if self.cards_sidebar_destroy.get(data[0]) != None:
                        self.cards_sidebar_destroy[data[0]].destroy()
                    else: 
                        self.mangas_to_read += 1
                    self.informative_text.configure(state='normal')
                    self.informative_text.delete(1.0, END)
                    self.informative_text.insert(1.0, f'Você tem um total de {self.mangas_to_read} \nmanga(s) para ler!\n{text_error}')
                    self.informative_text.configure(state='disabled')
                    card = CTkFrame(self.sidebar, width=130, height=50, fg_color='transparent')
                    card.pack(padx=10, pady=5)
                    self.cards_sidebar_destroy[data[0]] = card
                    self.cards_sidebar[data[0]] = card
                    btn_title = CTkButton(card, width=120, height=30, text=(data[1])[:16], command=lambda id=data[0]: self.show_manga(id))
                    btn_title.pack()
                    self.cards_sidebar[f'{data[0]} title'] = btn_title
                    chapters_frame = CTkFrame(card, width=80, height=30, border_width=1)
                    chapters_frame.pack()
                    remaing_chapters = CTkLabel(chapters_frame, width=80, height=30, text=f'+{len(chapters_to_read)}')
                    remaing_chapters.pack(padx=2, pady=(0,2))
                    self.cards_sidebar[f'{data[0]} chapters'] = remaing_chapters
                except:
                    self.error += 1
                    text_error = f'Erros: {self.error}'
                    self.informative_text.configure(state='normal')
                    self.informative_text.delete(1.0, END)
                    self.informative_text.insert(1.0, f'Você tem um total de {self.mangas_to_read} \nmanga(s) para ler!\n{text_error}')
                    self.informative_text.configure(state='disabled')
        threads.start()
        threads.join()
        if self.mangas_to_read == 0:
            self.informative_text.configure(state='normal')
            self.informative_text.delete(1.0, END)
            self.informative_text.insert(1.0, f'Você leu todos, LENDA!')
            self.informative_text.configure(state='disabled')
        self.reload_btn.configure(state='normal')

    def frame_change(self, frame:CTkFrame):
        if frame.winfo_exists(): frame.destroy()
        else: frame.pack()

    def add_manga(self):
        try:
            manga_name = self.fav_entry.get().split('/')[-2]
            manga_id = self.fav_entry.get().split('/')[-1]
        except: return False
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
        chapters = self.connection_data.get_data_chapters(manga[4])
        window_show = CTkToplevel()
        window_show.geometry('410x420+500+150')
        window_show.resizable(False, False)
        window_show.wm_title(manga[1])
        def destroy(window:CTk):
            while True:
                try: window.destroy()
                except: continue
                break
        window_show.protocol('WM_DELETE_WINDOW', lambda: destroy(window_show))
        type_reader = self.connection_data.get_config()['config']['reader-type']
        frame = CTkFrame(window_show, width=390, height=470)
        frame.pack(padx=10, pady=10)
        img = CTkImage(Image.open(manga[3]), size=(129, 204.1875))
        img_label = CTkLabel(frame, text=None, image=img)
        img_label.place(x=20,y=20)
        window_show.grab_set()
        next_chapter_frame = CTkFrame(frame, width=190, height=50)
        next_chapter_frame.place(x=170, y=20)
        next_chapter_place = CTkFrame(next_chapter_frame, width=160, height=30)
        next_chapter_place.place(x=15,y=10)
        def next_chapter(last_chapter:list) -> list:
            if chapters[0] == last_chapter: 
                return 'Todos lidos!'
            next_ch = None
            last_read = False
            chapters.reverse()
            for chapter in chapters:
                if last_read:
                    next_ch = chapter
                    break
                if chapter == last_chapter:
                    last_read = True
            chapters.reverse()
            if next_ch == None: next_ch = chapters[-1]
            return next_ch
        def read_chapter(chapter):
            self.connection_api.download_manga_chapter(chapter, manga[4])
            self.Reader(f'mangas/{manga[4]}/chapters/{chapter}', type_reader)

        next_ch = next_chapter([manga[2], self.connection_data.get_chapter_id(manga[4], manga[2])])
        text_ch = CTkLabel(next_chapter_place, text=next_ch[0] if next_ch != 'Todos lidos!' else next_ch)
        text_ch.place(x=10, y=3)
        btn_to_set = {}
        btn_set_readed = CTkButton(next_chapter_place, width=15, height=20,  text=None, image=self.img_view)
        btn_set_readed.configure(command=lambda: edit_last_read(next_chapter([self.connection_data.get_manga(manga_id)[2], self.connection_data.get_chapter_id(manga[4], self.connection_data.get_manga(manga_id)[2])])))
        btn_read = CTkButton(next_chapter_place, width=15, height=20,  text=None, image=self.img_read, command=lambda: read_chapter(self.connection_data.get_manga(manga_id)[2]))
        btn_read.place(x=85, y=4)
        btn_to_set['btn'] = btn_set_readed
        if text_ch._text != 'Todos lidos!':    
            btn_set_readed.place(x=120, y=4)
        tab_chapters = CTkTabview(frame, width=155, height=240)
        tab_chapters.place(x=170, y=70)
        def load_chapters():
            # match len(chapters):
            #     case 700 | 1400:
            #         cpt_per_frame = 200
            if len(chapters) > 700 and len(chapters) < 1400: cpt_per_frame = 200
            elif len(chapters) > 1400: cpt_per_frame = 600
            else: cpt_per_frame = 100
            tab_chapters.add('1')
            scroll_chapters = CTkScrollableFrame(tab_chapters.tab('1'), width=155, height=240)
            scroll_chapters.pack()
            is_read = False
            offset = 1
            num_chapter = 0
            for chapter in chapters:
                if self.end: return False
                if not window_show.winfo_exists(): return False
                try: frame_chapter = CTkFrame(scroll_chapters, width=150, height=30, border_color='white' if self.main_w._get_appearance_mode() == 'dark' else 'black', border_width=1)
                except: return False
                frame_chapter.pack(padx=5, pady=3)
                text = CTkLabel(frame_chapter, text=chapter[0])
                text.place(x=5, y=1)
                if not is_read:
                    if chapter[0] != manga[2]: 
                        img_btn = self.img_view
                    else: 
                        img_btn = self.img_not_view
                        is_read = True
                btn_set_read = CTkButton(frame_chapter, width=15, height=20,  text=None, image=img_btn)
                btn_set_read.configure(command=lambda number_ch=chapter, btn = btn_set_read: edit_last_read(number_ch, btn))
                btn_set_read.place(x=110, y=4)
                btn_read = CTkButton(frame_chapter, width=15, height=20,  text=None, image=self.img_read, command=lambda chapter=chapter[0]: read_chapter(chapter))
                btn_read.place(x=75, y=4)
                num_chapter += 1
                if num_chapter == cpt_per_frame:
                    offset += 1
                    sleep(0.1)
                    tab_chapters.add(str(offset))
                    scroll_chapters = CTkScrollableFrame(tab_chapters.tab(str(offset)), width=155, height=240)
                    scroll_chapters.pack()
                    num_chapter = 0
        Thread(target=load_chapters).start()
        def edit_last_read(chapter_read:list, btn:CTkButton=None):
            self.connection_data.set_manga(manga_id, 2, chapter_read[0])
            if btn != None: btn.configure(True, image=self.img_not_view)
            chapters_to_read = []
            for chapter in chapters:
                    if chapter == chapter_read: break
                    chapters_to_read.append(chapter)
            if self.cards_sidebar.get(manga_id) != None:
                if len(chapters_to_read) != 0:
                    self.cards_sidebar[f'{manga_id} chapters'].configure(text=f'+{len(chapters_to_read)}')
                else:
                    self.cards_sidebar[manga_id].destroy()
                    del[self.cards_sidebar[manga_id]]
                    self.mangas_to_read -= 1
                    text_error = f'Erros: {self.error}' if self.error != 0 else ''
                    self.informative_text.configure(state='normal')
                    self.informative_text.delete(1.0, END)
                    self.informative_text.insert(1.0, f'Você tem um total de {self.mangas_to_read} \nmanga(s) para ler!\n{text_error}')
                    self.informative_text.configure(state='disabled')
            else:
                if len(chapters_to_read) != 0:
                    card = CTkFrame(self.sidebar, width=130, height=50, fg_color='transparent')
                    card.pack(padx=10, pady=5)
                    self.cards_sidebar_destroy[manga[0]] = card
                    self.cards_sidebar[manga[0]] = card
                    btn_title = CTkButton(card, width=120, height=30, text=(manga[1])[:16], command=lambda id=manga[0]: self.show_manga(id))
                    btn_title.pack()
                    self.cards_sidebar[f'{manga[0]} title'] = btn_title
                    chapters_frame = CTkFrame(card, width=80, height=30, border_width=1)
                    chapters_frame.pack()
                    remaing_chapters = CTkLabel(chapters_frame, width=80, height=30, text=f'+{len(chapters_to_read)}')
                    remaing_chapters.pack(padx=2, pady=(0,2))
                    self.cards_sidebar[f'{manga[0]} chapters'] = remaing_chapters
                    self.mangas_to_read += 1
                    text_error = f'Erros: {self.error}' if self.error != 0 else ''
                    self.informative_text.configure(state='normal')
                    self.informative_text.delete(1.0, END)
                    self.informative_text.insert(1.0, f'Você tem um total de {self.mangas_to_read} \nmanga(s) para ler!\n{text_error}')
                    self.informative_text.configure(state='disabled')
            text_next = next_chapter(chapter_read)
            text_ch.configure(text=text_next[0] if text_next != 'Todos lidos!' else text_next)
            if text_ch._text == 'Todos lidos!':
                if btn_to_set.get('btn') != None:
                    if btn_to_set['btn'].winfo_exists():
                        btn_to_set['btn'].destroy()
            else:
                if btn_to_set.get('btn') != None:
                    if not btn_to_set['btn'].winfo_exists():
                        btn_set = CTkButton(next_chapter_place, width=15, height=20,  text=None, image=self.img_view)
                        btn_set.configure(command=lambda: edit_last_read(next_chapter([self.connection_data.get_manga(manga_id)[2], self.connection_data.get_chapter_id(manga[4], self.connection_data.get_manga(manga_id)[2])])))
                        btn_set.place(x=60, y=4)
                        btn_to_set['btn'] = btn_set
            
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
        def __init__(self, chapter_path:Path, type_reader:str) -> CTkToplevel:
            self.chapter_path = chapter_path
            self.type_reader = type_reader
            self.open()

        def open(self):
            match self.type_reader:
                case 'h-n':
                    self.horizontal()
                case _:
                    return False

        def horizontal(self):
            w_reader = CTkToplevel()
            w_reader.state('zoomed')
            w_reader.wm_title(str(self.chapter_path).split('/' if '/' in self.chapter_path else '\\')[-1])
            self.state = False
            def toggle_fullscreen(event=None):
                self.state = not self.state
                w_reader.attributes('-fullscreen', self.state)

            def end_fullscreen(event=None):
                self.state = False
                w_reader.attributes('-fullscreen', False)
                w_reader.bind('<Configure>', resize)


            w_reader.bind('<F11>', toggle_fullscreen)
            w_reader.bind('<Escape>', end_fullscreen)
            self.chapter_path = Path(self.chapter_path)
            manga_pages = []
            for i in self.chapter_path.glob('*'):
                if i.name.lower().endswith((
                        '.png',
                        '.jpg',
                        '.jpeg',
                        '.tiff',
                        '.bmp',
                        '.gif',
                        '.webp',
                        '.avif'
                )):
                    width = Image.open(i).width
                    height = Image.open(i).height
                    if width != height:
                        quotient = width / height
                    else:
                        quotient = 1
                    manga_pages.append(CTkImage(Image.open(i), size=(100*quotient, 100)))
            width = manga_pages[0]._size[0]
            height = manga_pages[0]._size[1]
            while width < w_reader.winfo_width() and height < w_reader.winfo_height():
                width *= 1.001
                height *= 1.001
            width = round(width, 0)
            height = round(height, 0)
            manga_pages[0].configure(size=(width, height))
            frame_chapter = CTkLabel(w_reader, image=manga_pages[0], text=None)
            frame_chapter.pack()
            w_reader.grab_set()
            self.page = 0


            def next_page(event=None):
                self.page += 1
                if self.page == len(manga_pages):
                    self.page -= 1
                    return False
                width = manga_pages[self.page]._size[0]
                height = manga_pages[self.page]._size[1]
                while width < w_reader.winfo_width() and height < w_reader.winfo_height():
                    width *= 1.001
                    height *= 1.001
                width = round(width, 0)
                height = round(height, 0)
                manga_pages[self.page].configure(size=(width, height))
                frame_chapter.configure(image=manga_pages[self.page])




            def previous_page(event=None):
                self.page -= 1
                if self.page < 0:
                    self.page += 1
                    return False
                width = manga_pages[self.page]._size[0]
                height = manga_pages[self.page]._size[1]
                while width < w_reader.winfo_width() and height < w_reader.winfo_height():
                    width *= 1.001
                    height *= 1.001
                width = round(width, 0)
                height = round(height, 0)
                manga_pages[self.page].configure(size=(width, height))
                frame_chapter.configure(image=manga_pages[self.page])




            w_reader.bind('<Right>', next_page)
            w_reader.bind('<Left>', previous_page)


            btn_next = CTkButton(w_reader, width=30, text='>', command=next_page)
            btn_next.place(x=0, y=w_reader.winfo_height()/2)


            def resize(event):
                width = manga_pages[self.page]._size[0]
                height = manga_pages[self.page]._size[1]
                if event != None:
                    if event.width == width and event.height == height:
                        return False
                if width > w_reader.winfo_width() or height > w_reader.winfo_height():
                    while width > w_reader.winfo_width() or height > w_reader.winfo_height():
                        width /= 1.001
                        height /= 1.001
                    width = round(width, 0)
                    height = round(height, 0)
                else:
                    while width < w_reader.winfo_width() and height < w_reader.winfo_height():
                        width *= 1.001
                        height *= 1.001
                    width = round(width, 0)
                    height = round(height, 0)
                manga_pages[self.page].configure(size=(width, height))
                frame_chapter.configure(image=manga_pages[self.page])


            w_reader.bind('<Configure>', resize)


            def motion(event):
                # print("Mouse position: (%s %s)" % (event.x, event.y))
                return True
            w_reader.bind('<Motion>', motion)


gui = MangaYouKnowGUI()
gui.run()
