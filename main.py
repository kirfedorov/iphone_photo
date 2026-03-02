import os
import re
import sys
import shutil
from pathlib import Path

def organize_current_folder():
    """
    Организует файлы из папок в текущей директории по годам и месяцам.
    Программа работает в той папке, где находится exe-файл.
    Формат исходных папок: ГГГГММ* (например, 202402__, 202309_c, 201706__Проект)
    Файлы переносятся в папки: Год/МесяцГод/
    """
    
    # Получаем путь к папке, где находится программа
    if getattr(sys, 'frozen', False):
        # Если программа скомпилирована в exe
        current_dir = Path(sys.executable).parent
    else:
        # Если запущена как скрипт Python
        current_dir = Path(__file__).parent
    
    # Словарь для перевода номеров месяцев в названия
    months_names = {
        '01': 'Январь',
        '02': 'Февраль',
        '03': 'Март',
        '04': 'Апрель',
        '05': 'Май',
        '06': 'Июнь',
        '07': 'Июль',
        '08': 'Август',
        '09': 'Сентябрь',
        '10': 'Октябрь',
        '11': 'Ноябрь',
        '12': 'Декабрь'
    }
    
    print("=" * 80)
    print("ПРОГРАММА ДЛЯ ОРГАНИЗАЦИИ ФАЙЛОВ ПО ГОДАМ И МЕСЯЦАМ")
    print("=" * 80)
    print(f"Рабочая папка: {current_dir}")
    print("\nФормат обрабатываемых папок: ГГГГММ* (например, 202402__, 202309_c, 201706__Проект)")
    print("Файлы будут перемещены в: Год/МесяцГод/")
    print("-" * 80)
    
    # Проверяем существование директории
    if not current_dir.exists():
        print(f"Ошибка: Директория не существует: {current_dir}")
        input("\nНажмите Enter для выхода...")
        return
    
    # Счетчики для статистики
    total_files_moved = 0
    processed_folders = 0
    skipped_folders = 0
    empty_folders = 0
    errors = 0
    created_years = set()
    created_months = set()
    
    print("Поиск папок для обработки...\n")
    
    # Проходим по всем элементам в текущей директории
    for item in sorted(current_dir.iterdir()):
        if item.is_dir():
            folder_name = item.name
            
            # Пропускаем уже созданные папки годов и месяцев
            if folder_name.endswith(" год") and folder_name[:-4].isdigit():
                continue
            # Пропускаем папки месяцев с годом
            if any(month in folder_name for month in months_names.values()) and any(char.isdigit() for char in folder_name):
                continue
            
            # Ищем год и месяц в имени папки - теперь поддерживает разные форматы
            # Ищем первые 6 цифр в имени папки (ГГГГММ)
            match = re.search(r'(\d{4})(\d{2})', folder_name)
            
            if match:
                year = match.group(1)
                month_num = match.group(2)
                
                # Проверяем, что месяц от 01 до 12
                if month_num not in months_names:
                    print(f"  [!] Неверный номер месяца ({month_num}) в папке: {folder_name}")
                    skipped_folders += 1
                    continue
                
                # Получаем название месяца
                month_name = months_names.get(month_num)
                
                # Создаем пути
                year_folder_name = f"{year} год"
                month_folder_name = f"{month_name}{year}"
                
                year_folder_path = current_dir / year_folder_name
                month_folder_path = year_folder_path / month_folder_name
                
                try:
                    # Создаем папку года, если нужно
                    if not year_folder_path.exists():
                        year_folder_path.mkdir(parents=True)
                        created_years.add(year)
                        print(f"  [+] Создана папка года: {year_folder_name}")
                    
                    # Создаем папку месяца с годом, если нужно
                    if not month_folder_path.exists():
                        month_folder_path.mkdir(parents=True)
                        created_months.add(f"{month_name}{year}")
                        print(f"  [+] Создана папка месяца: {month_folder_name}/")
                    
                    # Получаем список файлов в исходной папке
                    files = [f for f in item.iterdir() if f.is_file()]
                    
                    if not files:
                        print(f"  [-] Папка пуста: {folder_name}")
                        empty_folders += 1
                        # Удаляем пустую папку
                        try:
                            item.rmdir()
                            print(f"     Пустая папка удалена")
                        except:
                            pass
                        continue
                    
                    # Перемещаем каждый файл
                    files_moved = 0
                    for file_path in files:
                        # Создаем имя файла с префиксом из исходной папки для уникальности
                        base_name = file_path.stem
                        extension = file_path.suffix
                        
                        # Извлекаем суффикс из имени папки (часть после 6 цифр)
                        # Находим позицию после 6 цифр
                        match_pos = re.search(r'\d{6}', folder_name)
                        if match_pos:
                            suffix_start = match_pos.end()
                            folder_suffix = folder_name[suffix_start:].lstrip('_').strip()
                        else:
                            folder_suffix = ""
                        
                        # Формируем новое имя файла
                        if folder_suffix:
                            new_name = f"{base_name}_{folder_suffix}{extension}"
                        else:
                            new_name = file_path.name
                        
                        target_path = month_folder_path / new_name
                        
                        # Если файл с таким именем уже существует, добавляем номер
                        counter = 1
                        while target_path.exists():
                            if folder_suffix:
                                new_name = f"{base_name}_{folder_suffix}_{counter}{extension}"
                            else:
                                new_name = f"{base_name}_{counter}{extension}"
                            target_path = month_folder_path / new_name
                            counter += 1
                        
                        try:
                            shutil.move(str(file_path), str(target_path))
                            files_moved += 1
                            print(f"    [✓] {file_path.name} -> {year_folder_name}/{month_folder_name}/")
                        except Exception as e:
                            print(f"    [✗] Ошибка при перемещении {file_path.name}: {e}")
                            errors += 1
                    
                    total_files_moved += files_moved
                    processed_folders += 1
                    
                    # После перемещения всех файлов удаляем пустую папку
                    try:
                        # Проверяем, остались ли еще файлы или папки
                        remaining = list(item.iterdir())
                        if not remaining:
                            item.rmdir()
                            print(f"     Исходная папка {folder_name} удалена (пуста)")
                        else:
                            print(f"     В папке {folder_name} остались элементы: {len(remaining)}")
                    except Exception as e:
                        print(f"     Не удалось удалить папку {folder_name}: {e}")
                    
                except PermissionError:
                    print(f"  [✗] Ошибка доступа к папке: {folder_name}")
                    errors += 1
                except Exception as e:
                    print(f"  [✗] Ошибка при обработке папки {folder_name}: {e}")
                    errors += 1
            else:
                # Пропускаем папки не подходящего формата
                if not any(skip in folder_name for skip in [' год', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']):
                    print(f"  [-] Пропущена (нет даты): {folder_name}")
                    skipped_folders += 1
    
    # Выводим итоги
    print("\n" + "=" * 80)
    print("РЕЗУЛЬТАТЫ ОБРАБОТКИ")
    print("=" * 80)
    print(f"✓ Перемещено файлов: {total_files_moved}")
    print(f"✓ Обработано папок: {processed_folders}")
    print(f"− Пустых папок: {empty_folders}")
    print(f"− Пропущено папок: {skipped_folders}")
    print(f"✗ Ошибок: {errors}")
    
    if created_years:
        print(f"\nСозданы папки для годов: {', '.join(sorted(created_years))}")
    
    if created_months:
        months_list = sorted(list(created_months))
        print(f"Созданы папки для месяцев: {', '.join(months_list)}")
    
    print("\n" + "=" * 80)
    print("ГОТОВАЯ СТРУКТУРА ПАПОК:")
    print("=" * 80)
    
    # Показываем созданную структуру
    for year_folder in sorted(current_dir.iterdir()):
        if year_folder.is_dir() and year_folder.name.endswith(" год"):
            print(f"\n📁 {year_folder.name}/")
            for month_folder in sorted(year_folder.iterdir()):
                if month_folder.is_dir():
                    files = [f for f in month_folder.iterdir() if f.is_file()]
                    files_count = len(files)
                    print(f"  📁 {month_folder.name}/ ({files_count} файлов)")
                    # Показываем первые 3 файла в каждой папке месяца
                    count = 0
                    for file in sorted(files)[:3]:
                        print(f"    📄 {file.name}")
                    if files_count > 3:
                        print(f"    ... и еще {files_count - 3} файлов")
    
    print("\n" + "=" * 80)
    input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    try:
        organize_current_folder()
    except Exception as e:
        print(f"\nПроизошла критическая ошибка: {e}")
        input("\nНажмите Enter для выхода...")