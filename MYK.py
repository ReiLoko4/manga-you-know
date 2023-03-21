# why you see this trash project? I believe you can do more.

import csv

userManga = [
    7,
    'One Punch Man',
    'https://mangalivre.net/manga/one-punch-man/1036',
    '200',
    'C:/Users/ReiLoko4/Downloads/covers/one.jpg'
]

with open('database/data.csv', 'a+') as file:
    data = csv.writer(file, lineterminator='\n')
    data.writerow(userManga)

