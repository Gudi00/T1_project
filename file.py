import os

# Указанный путь к папке
folder_path = r'C:\Users\iosk0\Documents\СПО 2 сем\3 сем\ВМиКА лаб\lab2'

# Создаем папку, если она не существует (на всякий случай)
os.makedirs(folder_path, exist_ok=True)

# Создаем файлы от 1.m до 21.m
for i in range(22, 28):
    file_path = os.path.join(folder_path, f'{i}.m')
    with open(file_path, 'w') as f:
        pass  # Создаем пустой файл

print('Файлы успешно созданы!')