import PyInstaller.__main__
import os
import shutil

# Конфигурация
script_name = "main.py"  # Замените на имя вашего основного файла
exe_name = "CardManager"
icon_path = None  # Путь к иконке .ico (если нужна)
add_data = []

def build():
    # Формируем команды для PyInstaller
    cmd = [
        "--name={}".format(exe_name),
        "--onefile",
        "--windowed",
        "--clean",
        "--noconfirm",
        # "--icon={}".format(icon_path) if icon_path else "",
        "--add-data=assets;assets" if os.path.exists("assets") else "",
    ]
    
    # Добавляем дополнительные ресурсы
    for data in add_data:
        cmd.append(f"--add-data={data}")
    
    # Добавляем основной скрипт
    cmd.append(script_name)
    
    # Фильтруем пустые команды
    cmd = [arg for arg in cmd if arg]
    
    # Вызываем PyInstaller
    PyInstaller.__main__.run(cmd)
    
    # Копируем дополнительные файлы
    copy_additional_files()

def copy_additional_files():
    # Создаем папку для сборки
    dist_path = os.path.join("dist", exe_name)
    os.makedirs(dist_path, exist_ok=True)
    
    # Копируем примеры файлов колод
    example_decks = [
        "Сверхлюди.txt",
        "Примеры",
        "Импорт"
    ]
    
    for item in example_decks:
        if os.path.exists(item):
            dest = os.path.join(dist_path, item)
            if os.path.isdir(item):
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)
    
    print(f"\nФайлы скопированы в: {dist_path}")

if __name__ == "__main__":
    build()
    print("\nСборка завершена успешно!")
    print(f"Исполняемый файл находится в: dist/{exe_name}.exe")