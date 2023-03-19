# Graphic User Interface for the project

from customtkinter import *
from PIL import Image
import csv
from math import ceil


set_appearance_mode('System')
set_default_color_theme('green')

def window_close():
    root.iconify()

root = CTk()
root.geometry('800x550')
root.resizable(width=False, height=False)
root.wm_title('Manga You Know')
root.iconbitmap(bitmap='assets/pasta_vermelha.ico')

tabs = CTkTabview(master=root, width=600, height=450)
tabs.pack()
tabs.add('Favoritos')
tabs.add('Adicionar')
tabs.add('Configurações')


# Favoritos display

with open('data.csv', mode='r') as data_csv:
    leitor_csv = csv.reader(data_csv)
    data = []
    for linha in leitor_csv:
        data.append(linha)
del[data[0]]

tabfav = CTkScrollableFrame(master=tabs.tab('Favoritos'), width=600, height=20000)
tabfav.pack()

editar = CTkImage(Image.open('C:/Users/ReiLoko4/Downloads/editar.ico'), size=(15,15))

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
    buttonedit1 = CTkButton(master=card1, text='', width=15, image=editar, fg_color='white')
    buttonedit1.place(x=123, y=235)

    count+=1
    try:
        if str(count+1) in data[count][0]:
            card2 = CTkFrame(master=tabfav, width=160, height=270)
            card2.place(x=180, y=space)
            capa2 = CTkImage(Image.open(data[count][4]), size=(145, 220))
            img2 = CTkLabel(master=card2, text='', image=capa2, width=140, height=150)
            img2.place(x=8, y=6)
            button2 = CTkButton(master=card2, text='Ver capítulos', width=107)
            button2.place(x=8, y=235)
            buttonedit2 = CTkButton(master=card2, text='', width=15, image=editar, fg_color='white')
            buttonedit2.place(x=123, y=235)


            count+=1
            try:
                if str(count + 1) in data[count][0]:
                    card3 = CTkFrame(master=tabfav, width=160, height=270)
                    card3.place(x=355,y=space)
                    capa3 = CTkImage(Image.open(data[count][4]), size=(145, 220))
                    img3 = CTkLabel(master=card3, text='', image=capa3, width=140, height=150)
                    img3.place(x=8, y=6)
                    button3 = CTkButton(master=card3, text='Ver capítulos', width=100)
                    button3.place(x=8, y=235)
                    buttonedit3 = CTkButton(master=card3, text='', width=15, image=editar, fg_color='white')
                    buttonedit3.place(x=123, y=235)
                    count+=1
            except Exception:
                break
    except Exception:
        break            
    space+=290

btn = CTkButton(master=tabfav, text='sumir', command=window_close)
btn.pack()

# Adicionar display


new_fav = CTkEntry(master=tabs.tab('Adicionar'), placeholder_text='https://mangalivre.net/genero/nomeDoManga/idDoManga', width=330)
new_fav.pack(pady=13,padx=13)


# Configurações display


always_donwload = CTkCheckBox(master=tabs.tab('Configurações'), text='Sempre baixar novos capítulos')
always_donwload.pack(pady=13, padx=13)
save = CTkButton(master=tabs.tab('Configurações'), text='Salvar')
save.pack(pady=13, padx=13)



root.mainloop()