# Graphic User Interface for the project

from customtkinter import *
from tkinter import filedialog
from pathlib import Path
from PIL import Image
import csv
from math import ceil, floor


set_appearance_mode('System')
set_default_color_theme('green')

root = CTk()
root.geometry('800x550+300+80')
root.resizable(width=False, height=False)
root.wm_title('Manga You Know')
root.wm_iconbitmap('assets/pasta_vermelha.ico')



tabs = CTkTabview(master=root, width=600, height=545)
tabs.pack()
tabs.add('Favoritos')
tabs.add('Adicionar')
tabs.add('Configurações')


# # # Favoritos display

# open my 'database'
with open('database/data.csv', mode='r') as data_csv:
    leitor_csv = csv.reader(data_csv)
    data = []
    for linha in leitor_csv:
        data.append(linha)
# delete the line 1 because this is just the name of the columns
del[data[0]]

# manga reader
page_index = 0
def reader_open():
    reader = CTkToplevel(root)
    reader.geometry('840x545+300+80')
    reader.resizable(width=False, height=False)
    reader.wm_title('Reader')
    reader.wm_iconbitmap('assets/pasta_vermelha.ico')
    reader.config(bg='black')


    # Caminho para a pasta que contém as imagens
    path = Path('C:/Users/ReiLoko4/Manga Livre DL/One Punch Man/Chapter 216/')
    manga_pages = []
    for i in path.glob('*'):
        if i.name.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.webp')):
            page = Image.open(i)
            double_page = False
            if page.width > page.height: double_page = True
            manga_pages.append([i, page.width, page.height, double_page])
    if manga_pages[0][3]:
        img_w = manga_pages[0][1]
        img_h = manga_pages[0][2]
        while img_w > 760 or img_h > 545:
            img_w = img_w/1.005
            img_h = img_h/1.005
        print(img_w)
        page_1_img = CTkImage(Image.open(manga_pages[0][0]), size=(img_w, img_h))
        page_1 = CTkLabel(reader, text=None, image=page_1_img, width=img_w, height=545, bg_color='black')
        page_1.place(x=floor(800-img_w), y=0)
    elif manga_pages[1][3]:
        img_w = manga_pages[0][1]
        img_h = manga_pages[0][2]
        if (img_w < 380 or img_h < 545):
            img_w *= 5
            img_h *= 5
        while img_w > 380 or img_h > 545:
            img_w /= 1.005
            img_h /= 1.005
        page_1_img = CTkImage(Image.open(manga_pages[0][0]), size=(img_w, img_h))
        page_1 = CTkLabel(reader, text=None, image=page_1_img, width=760, height=545, bg_color='black')
        page_1.place(x=60, y=0)
    else:
        img_1_w = manga_pages[0][1]
        img_2_w = manga_pages[1][1]
        img_1_h = manga_pages[0][2]
        img_2_h = manga_pages[1][2]
        while (img_1_w > 380 or img_1_h > 545 or
               img_2_w > 380 or img_2_h > 545):
            img_1_w /= 1.005
            img_2_w /= 1.005
            img_1_h /= 1.005
            img_2_h /= 1.005
        print(f'{img_1_w} {img_2_w}')
        page_1_img = CTkImage(Image.open(manga_pages[0][0]), size=(img_1_w, img_1_h))
        page_2_img = CTkImage(Image.open(manga_pages[1][0]), size=(img_2_w, img_2_h))
        page_1 = CTkLabel(reader, text=None, image=page_1_img, width=img_1_w, height=545, bg_color='black')
        page_2 = CTkLabel(reader, text=None, image=page_2_img, width=img_2_w, height=545, bg_color='black')
        # japanese format lol
        page_1.place(x=floor(801-img_2_w), y=0)
        page_2.place(x=ceil(420-img_1_w), y=0)

    previous_img = CTkImage(Image.open('C:/Users/ReiLoko4/Downloads/next.ico'), size=(13,20))
    next_img = CTkImage(Image.open('C:/Users/ReiLoko4/Downloads/previous.ico'), size=(13,20))
    previous_btn = CTkButton(reader, width=13, height=50, text=None, image=next_img,)
    next_btn = CTkButton(reader, width=13, height=50, text=None, image=previous_img,)
    previous_btn.place(x=5, y=272)
    next_btn.place(x=807, y=272)

    reader.grab_set()
    root.withdraw()
    def reaper(window):
        global page_index
        page_index = 0
        window.destroy()
        reader.grab_release()
        if root.state != 'normal': root.deiconify()
    reader.protocol('WM_DELETE_WINDOW', lambda: reaper(reader))

# manga options
def options_window(id_database):
    window = CTkToplevel(tabfav)
    window.geometry('400x400+500+200')
    window.title('Options')
    for i in range(len(data)):
        if(str(id_database) == data[i][0]): config = data[i]
    print(config)
    window.grab_set()
    def reaper(window_out):
        window_out.destroy()
        window.grab_release()
        if root.state != 'normal': root.deiconify()
    window.protocol('WM_DELETE_WINDOW', lambda: reaper(window))
        

class FolderSelector(CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self.path_entry = CTkEntry(self, width=200, state=DISABLED)
        self.path_entry.pack(side=LEFT, padx=5, pady=5)

        self.select_button = CTkButton(self, text="Selecionar pasta", command=self.select_folder)
        self.select_button.pack(side=LEFT, padx=5, pady=5)

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if len(folder_path) != 0:
            self.path_entry.configure(state=NORMAL)
            self.path_entry.delete(0, END)
            self.path_entry.insert(0, folder_path)
            self.path_entry.configure(state=DISABLED)

    def get_folder_path(self):
        return self.path_entry.get()



# manga more
#        

tabfav = CTkScrollableFrame(master=tabs.tab('Favoritos'), width=550, height=20000)
tabfav.pack()

edit = CTkImage(Image.open('C:/Users/ReiLoko4/Downloads/editar.ico'), size=(15,15))

trash = CTkImage(Image.open('C:/Users/ReiLoko4/Downloads/lixo.ico'), size=(15,20))



space = 10
count = 0
for i in range(ceil((len(data)) /3)):
    card1 = CTkFrame(master=tabfav, width=160, height=270)
    card1.pack(anchor='w', pady=10, padx=5)
    capa1 = CTkImage(Image.open(data[count][4]), size=(145, 220))
    img1 = CTkLabel(master=card1, text='', image=capa1, width=140, height=150)
    img1.place(x=8, y=6)
    button1 = CTkButton(master=card1, text='Ver capítulos', width=107)
    button1.place(x=8, y=235)
    buttonedit1 = CTkButton(master=card1, text=None, width=15, image=edit, fg_color='white', command=lambda count=count: options_window(count))
    buttonedit1.place(x=123, y=235)

    count+=1
    try:
        if str(count) in data[count][0]:
            card2 = CTkFrame(master=tabfav, width=160, height=270)
            card2.place(x=180, y=space)
            capa2 = CTkImage(Image.open(data[count][4]), size=(145, 220))
            img2 = CTkLabel(master=card2, text=None, image=capa2, width=140, height=150)
            img2.place(x=8, y=6)
            button2 = CTkButton(master=card2, text='Ver capítulos', width=107)
            button2.place(x=8, y=235)
            buttonedit2 = CTkButton(master=card2, text=None, width=15, image=edit, fg_color='white', command=lambda count=count: options_window(count))
            buttonedit2.place(x=123, y=235)


            count+=1
            if str(count) in data[count][0]:
                card3 = CTkFrame(master=tabfav, width=160, height=270)
                card3.place(x=355,y=space)
                capa3 = CTkImage(Image.open(data[count][4]), size=(145, 220))
                img3 = CTkLabel(master=card3, text='', image=capa3, width=140, height=150)
                img3.place(x=8, y=6)
                button3 = CTkButton(master=card3, text='Ver capítulos', width=107)
                button3.place(x=8, y=235)
                buttonedit3 = CTkButton(master=card3, text='', width=15, image=edit, fg_color='white', command=lambda count=count: options_window(count))
                buttonedit3.place(x=123, y=235)
                count+=1
            
    except Exception:
        break            
    space+=290

btn = CTkButton(master=tabfav, text='Abrir leitor', command=reader_open)
btn.pack()



# # # Adicionar display


new_fav = CTkEntry(master=tabs.tab('Adicionar'), placeholder_text='https://mangalivre.net/genero/nomeDoManga/idDoManga', width=330)
new_fav.pack(pady=13,padx=13)


# # # Configurações display


always_donwload = CTkCheckBox(master=tabs.tab('Configurações'), text='Sempre baixar novos capítulos')
always_donwload.pack(pady=13, padx=13)
save = CTkButton(master=tabs.tab('Configurações'), text='Salvar')
save.pack(pady=13, padx=13)

def import_perfil(folder_path):
    print(folder_path + ' importado')

load_perfil = CTkLabel(tabs.tab('Configurações'), text='Importar perfil')
load_perfil.pack()
folder_selector = FolderSelector(tabs.tab('Configurações'))
folder_selector.pack()
run_import_perfil = CTkButton(tabs.tab('Configurações'), text='Importar', command=lambda: import_perfil(folder_selector.get_folder_path()))
run_import_perfil.pack()

root.mainloop()