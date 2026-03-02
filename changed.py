import os
import re
import sys
from pathlib import Path

def rename_folders_recursively():
    """
    Программа рекурсивно обходит все папки и переименовывает вложенные папки
    из формата ГГГГММ__ в формат МесяцГГГГ.
    Например: 202602__ -> Февраль2026
    Работает начиная с той папки, где находится exe-файл.
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
    print("ПРОГРАММА ДЛЯ РЕКУРСИВНОГО ПЕРЕИМЕНОВАНИЯ ПАПОК")
    print("=" * 80)
    print(f"Стартовая папка: {current_dir}")
    print("\nБудут обработаны ВСЕ вложенные папки с форматом ГГГГММ__")
    print("Формат исходных папок: ГГГГММ__ (например, 202602__, 202309__)")
    print("Новый формат: МесяцГГГГ (например, Февраль2026, Сентябрь2023)")
    print("-" * 80)
    
    # Проверяем существование директории
    if not current_dir.exists():
        print(f"Ошибка: Директория не существует: {current_dir}")
        input("\nНажмите Enter для выхода...")
        return
    
    # Счетчики для статистики
    total_renamed = 0
    total_skipped = 0
    total_errors = 0
    processed_folders = 0
    
    print("Начинаем рекурсивный обход папок...\n")
    
    # Рекурсивно обходим все папки
    for root, dirs, files in os.walk(current_dir):
        current_path = Path(root)
        
        # Пропускаем корневую папку при первом проходе?
        # Но нам нужно обрабатывать папки на всех уровнях
        
        # Обрабатываем каждую папку в текущей директории
        for dir_name in dirs[:]:  # Используем копию списка, т.к. будем изменять
            folder_path = current_path / dir_name
            
            # Проверяем формат: 6 цифр и два подчеркивания (может быть что-то после)
            match = re.match(r'^(\d{4})(\d{2})__', dir_name)
            
            if match:
                year = match.group(1)
                month_num = match.group(2)
                
                # Проверяем, что месяц от 01 до 12
                if month_num not in months_names:
                    print(f"  [!] Неверный номер месяца ({month_num}) в папке: {folder_path}")
                    total_skipped += 1
                    continue
                
                # Получаем название месяца
                month_name = months_names.get(month_num)
                
                # Получаем остаток имени после 6 цифр и подчеркиваний
                remaining = dir_name[8:]  # пропускаем первые 8 символов (6 цифр + 2 подчеркивания)
                
                # Формируем новое имя
                if remaining:
                    # Если есть остаток, добавляем его через подчеркивание
                    new_name = f"{month_name}{year}_{remaining}"
                else:
                    # Если только дата, просто месяц+год
                    new_name = f"{month_name}{year}"
                
                # Полный путь к новой папке
                new_path = current_path / new_name
                
                try:
                    # Проверяем, не существует ли уже папка с таким именем
                    if new_path.exists():
                        print(f"  [!] Папка {new_name} уже существует, пропускаем: {folder_path}")
                        total_skipped += 1
                        continue
                    
                    # Переименовываем папку
                    folder_path.rename(new_path)
                    print(f"  [✓] {folder_path} -> {new_name}")
                    total_renamed += 1
                    
                    # Обновляем список dirs, чтобы продолжить обход с новым именем
                    # Но это не обязательно, т.к. мы уже обработали эту папку
                    
                except PermissionError:
                    print(f"  [✗] Ошибка доступа: {folder_path}")
                    total_errors += 1
                except Exception as e:
                    print(f"  [✗] Ошибка при переименовании {folder_path}: {e}")
                    total_errors += 1
        
        processed_folders += 1
        if processed_folders % 100 == 0:
            print(f"  ... обработано {processed_folders} папок, найдено изменений: {total_renamed}")
    
    # Выводим итоги
    print("\n" + "=" * 80)
    print("РЕЗУЛЬТАТЫ ПЕРЕИМЕНОВАНИЯ")
    print("=" * 80)
    print(f"✓ Переименовано папок: {total_renamed}")
    print(f"− Пропущено папок: {total_skipped}")
    print(f"✗ Ошибок: {total_errors}")
    print(f"📁 Обработано директорий: {processed_folders}")
    
    print("\n" + "=" * 80)
    input("Нажмите Enter для выхода...")

def preview_changes():
    """
    Режим предпросмотра - показывает, какие папки будут переименованы,
    но не выполняет реальных изменений.
    """
    
    # Получаем текущую папку
    if getattr(sys, 'frozen', False):
        current_dir = Path(sys.executable).parent
    else:
        current_dir = Path(__file__).parent
    
    # Названия месяцев
    months = {
        '01': 'Январь', '02': 'Февраль', '03': 'Март',
        '04': 'Апрель', '05': 'Май', '06': 'Июнь',
        '07': 'Июль', '08': 'Август', '09': 'Сентябрь',
        '10': 'Октябрь', '11': 'Ноябрь', '12': 'Декабрь'
    }
    
    print("=" * 80)
    print("РЕЖИМ ПРЕДПРОСМОТРА (изменения не выполняются)")
    print("=" * 80)
    print(f"Стартовая папка: {current_dir}")
    print("-" * 80)
    
    found_folders = 0
    
    # Рекурсивно обходим все папки
    for root, dirs, files in os.walk(current_dir):
        current_path = Path(root)
        
        for dir_name in dirs:
            folder_path = current_path / dir_name
            
            # Проверяем формат
            match = re.match(r'^(\d{4})(\d{2})__', dir_name)
            
            if match:
                year = match.group(1)
                month_num = match.group(2)
                month_name = months.get(month_num)
                
                if month_name:
                    remaining = dir_name[8:]
                    if remaining:
                        new_name = f"{month_name}{year}_{remaining}"
                    else:
                        new_name = f"{month_name}{year}"
                    
                    # Относительный путь для компактности
                    rel_path = folder_path.relative_to(current_dir)
                    print(f"  [?] {rel_path} -> {new_name}")
                    found_folders += 1
                else:
                    rel_path = folder_path.relative_to(current_dir)
                    print(f"  [!] {rel_path} -> неверный месяц {month_num}")
                    found_folders += 1
    
    print("-" * 80)
    print(f"Найдено папок для переименования: {found_folders}")
    print("=" * 80)
    input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    print("Выберите режим работы:")
    print("1. Реальное переименование (рекурсивно)")
    print("2. Предпросмотр (без изменений)")
    print("3. Выход")
    
    choice = input("\nВаш выбор (1/2/3): ").strip()
    
    try:
        if choice == '1':
            rename_folders_recursively()
        elif choice == '2':
            preview_changes()
        else:
            print("Выход...")
    except Exception as e:
        print(f"\nПроизошла критическая ошибка: {e}")
        input("\nНажмите Enter для выхода...")