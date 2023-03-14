# Graphic User Interface for the project

import customtkinter as ctk


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

def print_nothing_to_use():
    print("nothing")

root = ctk.CTk()
root.geometry("700x450")
root.resizable(width=False, height=False)
root.wm_title("Manga You Know")
root.iconbitmap(bitmap="assets/pasta_vermelha.ico")


frame = ctk.CTkFrame(master=root, width=200, height=400).place(x=90, y=9)

label = ctk.CTkLabel(master=frame, text="Downloand any mangas from Manga Livre")
label.pack(pady=12, padx=10)

input = ctk.CTkEntry(master=frame, placeholder_text="Manga link")
input.pack(pady=12, padx=10)

button = ctk.CTkButton(master=frame, text="Procurar", command=print_nothing_to_use)
button.pack(pady=12, padx=10)

checkbox = ctk.CTkCheckBox(master=frame, text="Save all mangas")
checkbox.pack(pady=12, padx=10)

root.mainloop()