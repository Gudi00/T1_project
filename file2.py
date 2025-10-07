import os

# Указанный путь к папке
folder_path = r'C:\Users\iosk0\Documents\СПО 2 сем\3 сем\ВМиКА лаб\lab2'

# Проверяем, существует ли папка
if not os.path.exists(folder_path):
    print(f"Папка {folder_path} не существует!")
    exit()

# Переименовываем файлы от 1.m до 21.m
for i in range(1, 28):
    old_file = os.path.join(folder_path, f'{i}.m')
    new_file = os.path.join(folder_path, f'a{i}.m')

    # Проверяем, существует ли старый файл
    if os.path.exists(old_file):
        os.rename(old_file, new_file)
        print(f"Файл {old_file} переименован в {new_file}")
    else:
        print(f"Файл {old_file} не найден")

print("Переименование завершено!")