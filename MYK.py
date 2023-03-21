# why you see this trash project? I believe you can do more.

from manga_livre_dl import MangaLivreDl as md
import csv

userManga = [
    7,
    'One Punch Man',
    'https://mangalivre.net/manga/one-punch-man/1036',
    '200',
    'C:/Users/ReiLoko4/Downloads/covers/one.jpg'
]

with open('data.csv', 'a+') as file:
    data = csv.writer(file, lineterminator='\n')
    data.writerow(userManga)

