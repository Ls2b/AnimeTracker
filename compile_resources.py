import os
import re
import base64

print("--- НАЧАЛО АВТОНОМНОЙ СБОРКИ РЕСУРСОВ ---")

qrc_file = "sprites.qrc"
output_file = "sprites_rc.py"

if not os.path.exists(qrc_file):
    print(f"ОШИБКА: Файл {qrc_file} не найден!")
    input("\nНажмите Enter для выхода...")
    exit()

try:
    with open(qrc_file, "r", encoding="utf-8") as f:
        qrc_content = f.read()
    
    # Ищем все файлы внутри тегов <file>...</file>
    files = re.findall(re.compile(r"<file>(.*?)</file>"), qrc_content)
    
    if not files:
        print("В файле .qrc не найдено путей к картинкам.")
        exit()

    resources = {}
    for file_path in files:
        normalized_path = file_path.strip().replace("\\", "/")
        if os.path.exists(normalized_path):
            with open(normalized_path, "rb") as img_f:
                # Кодируем картинку в байты
                resources[normalized_path] = base64.b64encode(img_f.read()).decode('utf-8')
            print(f"Успешно упакован: {normalized_path}")
        else:
            print(f"ПРЕДУПРЕЖДЕНИЕ: Файл не найден на диске: {normalized_path}")

    # Генерируем аналог pyrcc файла, который понимает PyQt6
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Файл сгенерирован автоматически без pyrcc\n")
        f.write("from PyQt6.QtCore import qRegisterResourceData\n")
        f.write("import base64\n\n")
        
        # Переводим данные в бинарный вид для Qt внутреннего хранилища
        f.write("resource_data = {\n")
        for path, data_b64 in resources.items():
            f.write(f"    'icons/{path}': base64.b64decode('{data_b64}'),\n")
        f.write("}\n\n")
        
        # Подменяем стандартный поиск ресурсов Qt, чтобы он читал из нашего словаря
        f.write("from PyQt6.QtGui import QPixmap, QIcon\n")
        f.write("_old_qicon_init = QIcon.__init__\n")
        f.write("def _new_qicon_init(self, *args, **kwargs):\n")
        f.write("    if args and isinstance(args[0], str) and args[0].startswith(':/'):\n")
        f.write("        key = args[0].lstrip(':/')\n")
        f.write("        if key in resource_data:\n")
        f.write("            pix = QPixmap()\n")
        f.write("            pix.loadFromData(resource_data[key])\n")
        f.write("            _old_qicon_init(self, pix)\n")
        f.write("            return\n")
        f.write("    _old_qicon_init(self, *args, **kwargs)\n")
        f.write("QIcon.__init__ = _new_qicon_init\n")

    print("----------------------------------------")
    print(f"УСПЕХ! Родной файл ресурсов {output_file} успешно создан!")

except Exception as e:
    print(f"Произошла непредвиденная ошибка: {e}")

input("\nНажмите Enter для завершения...")