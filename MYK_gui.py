# Graphic User Interface for the project

from customtkinter import *
from PIL import Image
from MYK import *

set_appearance_mode("System")
set_default_color_theme("green")

def window_close():
    root.iconify()

root = CTk()
root.geometry("800x550")
root.resizable(width=False, height=False)
root.wm_title("Manga You Know")
root.iconbitmap(bitmap="assets/pasta_vermelha.ico")

tabs = CTkTabview(master=root, width=600, height=450)
tabs.pack()
tabs.add("Favoritos")
tabs.add("Adicionar")
tabs.add("Configurações")


# Favoritos display


tabfav = CTkScrollableFrame(master=tabs.tab("Favoritos"), width=600, height=20000)
tabfav.pack()

capa = CTkImage(Image.open("C:/Users/thiag/Downloads/onepiece.jpg"), size=(145, 220))
editar = CTkImage(Image.open("C:/Users/thiag/Downloads/editar.ico"), size=(15,15))

space = 10
for i in range(3):
    card1 = CTkFrame(master=tabfav, width=160, height=270)
    card1.pack(anchor="w", pady=10, padx=5)
    img1 = CTkLabel(master=card1, text="", image=capa, width=140, height=150)
    img1.place(x=8, y=6)
    button1 = CTkButton(master=card1, text="Ver capítulos", width=107)
    button1.place(x=8, y=235)
    buttonedit1 = CTkButton(master=card1, text="", width=15, image=editar, fg_color="white")
    buttonedit1.place(x=123, y=235)
    card2 = CTkFrame(master=tabfav, width=160, height=220)
    card2.place(x=180, y=space)
    button2 = CTkButton(master=card2, text="Ver capítulos", width=100)
    button2.place(x=9, y=185)
    card3 = CTkFrame(master=tabfav, width=160, height=220)
    card3.place(x=355,y=space)
    button3 = CTkButton(master=card3, text="Ver capítulos", width=100)
    button3.place(x=9, y=185)
    space+=240


# Adicionar display


new_fav = CTkEntry(master=tabs.tab("Adicionar"), placeholder_text="https://mangalivre.net/genero/nomeDoManga/idDoManga", width=330)
new_fav.pack(pady=13,padx=13)


# Configurações display


always_donwload = CTkCheckBox(master=tabs.tab("Configurações"), text="Sempre baixar novos capítulos")
always_donwload.pack(pady=13, padx=13)
save = CTkButton(master=tabs.tab("Configurações"), text="Salvar")
save.pack(pady=13, padx=13)

btn = CTkButton(master=tabfav, text="sumir", command=window_close)
btn.pack()

root.mainloop()