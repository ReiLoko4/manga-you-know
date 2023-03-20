# Graphic User Interface for the project

from customtkinter import *
from PIL import Image
import csv
from math import ceil


set_appearance_mode('System')
set_default_color_theme('green')

root = CTk()
root.geometry('800x550')
root.resizable(width=False, height=False)
root.wm_title('Manga You Know')
root.iconbitmap('assets/pasta_vermelha.ico')



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

page_index = 0
def reader_open():
    reader = CTkToplevel(root)
    reader.geometry('800x545')
    reader.resizable(width=False, height=False)
    reader.wm_title('Reader')
    reader.iconbitmap(bitmap='assets/pasta_vermelha.ico')

    def previous_page(page_index_out):
        
        global page_index
        page_index=page_index_out
        page_index-=2
        if (page_index < 0):
            print('no more chapters, bitch')
            page_index+=2
        else:
            page_img1 = CTkImage(Image.open(f'C:/Users/ReiLoko4/Manga Livre DL/One Piece/Chapter 1/{page_index+1}.jpg'), size=(350,545))
            page1 = CTkLabel(reader, width=350, height=545, text='', image=page_img1)
            page_img2 = CTkImage(Image.open(f'C:/Users/ReiLoko4/Manga Livre DL/One Piece/Chapter 1/{page_index}.jpg'), size=(350, 545))
            page2 = CTkLabel(reader, width=350, height=545, text='', image=page_img2)
            page1.place(x=49, y=0)
            page2.place(x=401, y=0)


    def next_page(page_index_out):
        global page_index
        page_index=page_index_out
        page_index+=2
        try:
            page_img1 = CTkImage(Image.open(f'C:/Users/ReiLoko4/Manga Livre DL/One Piece/Chapter 1/{page_index+1}.jpg'), size=(350,545))
            page1 = CTkLabel(reader, width=350, height=545, text='', image=page_img1)
            page_img2 = CTkImage(Image.open(f'C:/Users/ReiLoko4/Manga Livre DL/One Piece/Chapter 1/{page_index}.jpg'), size=(350, 545))
            page2 = CTkLabel(reader, width=350, height=545, text='', image=page_img2)
            page1.place(x=49, y=0)
            page2.place(x=401, y=0)
        except Exception:
            print('you read the last page, lol')
            page_index-=2

    page_img1 = CTkImage(Image.open(f'C:/Users/ReiLoko4/Manga Livre DL/One Piece/Chapter 1/0.jpg'), size=(350,545))
    page1 = CTkLabel(reader, width=350, height=545, text='', image=page_img1)
    page_img2 = CTkImage(Image.open(f'C:/Users/ReiLoko4/Manga Livre DL/One Piece/Chapter 1/1.jpg'), size=(350, 545))
    page2 = CTkLabel(reader, width=350, height=545, text='', image=page_img2)
    page1.place(x=401, y=0)
    page2.place(x=49, y=0)

   
    previous_img = CTkImage(Image.open('C:/Users/ReiLoko4/Downloads/next.ico'), size=(13,20))
    next_img = CTkImage(Image.open('C:/Users/ReiLoko4/Downloads/previous.ico'), size=(13,20))
    previous_btn = CTkButton(reader, width=13, height=50, text=None, image=next_img, command=lambda: next_page(page_index))
    next_btn = CTkButton(reader, width=13, height=50, text=None, image=previous_img, command=lambda: previous_page(page_index))
    previous_btn.place(x=5, y=272)
    next_btn.place(x=765, y=272)
    reader.grab_set()
    root.withdraw()
    def reaper(window):
        global page_index
        page_index = 0
        window.destroy()
        reader.grab_release()
        if root.state != 'normal': root.deiconify()
    reader.protocol('WM_DELETE_WINDOW', lambda: reaper(reader))


def options_window(id_database):
    window = CTkToplevel(tabfav)
    window.geometry('400x400')
    window.title('Options')
    for i in range(len(data)):
        if(str(id_database) == data[i][0]): config = data[i]
    print(config)
        
    

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

root.mainloop()