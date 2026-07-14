import json
from typing import List, Dict, Any, Optional, Union

from datetime import datetime
from datetime import timedelta

def extract_shipment_date(
    value: any, 
    return_as_string: bool = True,
    date_format: str = '%Y-%m-%d'
) -> Union[str, Optional[datetime], None]:
    """
    Извлекает дату отгрузки из значения ячейки с обработкой разных форматов.
    
    Args:
        value: Значение ячейки (может быть str, int, float, None)
        return_as_string: Если True - возвращает строку, если False - datetime объект
        date_format: Формат для строкового вывода (по умолчанию '%Y-%m-%d')
    
    Returns:
        Строка с датой, datetime объект или None (если значение пустое)
    
    Примеры:
        >>> extract_shipment_date('2026-07-14')
        '2026-07-14'
        >>> extract_shipment_date('14.07.2026')
        '2026-07-14'
        >>> extract_shipment_date(46216)  # Excel формат
        '2026-07-14'
        >>> extract_shipment_date('')
        ''
        >>> extract_shipment_date(None)
        ''
    """
    # Проверяем пустые значения
    if value is None or str(value).strip() == '':
        return "" if return_as_string else None
    
    # Приводим к строке
    value_str = str(value).strip()
    
    # Если это число (Excel формат)
    try:
        # Пробуем преобразовать в число
        numeric_value = float(value_str)
        if numeric_value > 0:
            # Excel даты: количество дней с 1900-01-01
            # Корректировка для Excel (1900-01-01 = 1)
            base_date = datetime(1899, 12, 30)
            parsed_date = base_date + timedelta(days=numeric_value)
            if return_as_string:
                return parsed_date.strftime(date_format)
            return parsed_date
    except (ValueError, TypeError):
        pass
    
    # Список поддерживаемых форматов дат
    date_formats = [
        '%Y-%m-%d',           # 2026-07-14
        '%d.%m.%Y',           # 14.07.2026
        '%m/%d/%Y',           # 07/14/2026
        '%d/%m/%Y',           # 14/07/2026
        '%Y%m%d',             # 20260714
        '%d-%m-%Y',           # 14-07-2026
        '%m-%d-%Y',           # 07-14-2026
        '%Y.%m.%d',           # 2026.07.14
        '%d.%m.%y',           # 14.07.26
        '%d/%m/%y',           # 14/07/26
        '%d-%m-%y',           # 14-07-26
        '%d %b %Y',           # 14 Jul 2026
        '%d %B %Y',           # 14 July 2026
        '%b %d, %Y',          # Jul 14, 2026
        '%B %d, %Y',          # July 14, 2026
    ]
    
    # Пробуем парсить разные форматы дат
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(value_str, fmt)
            if return_as_string:
                return parsed_date.strftime(date_format)
            return parsed_date
        except ValueError:
            continue
    
    # Если ничего не подошло, возвращаем исходное значение
    return value_str if return_as_string else None

def find_nakl_numbers(
    nakl_search: str, 
    data_file: str = 'base_data.json',
    case_sensitive: bool = False,
    include_shipment_date: bool = True
) -> Union[List[str], List[Dict[str, Any]]]:
    """
    Ищет все номера накладных (column21), которые содержат искомую подстроку.
    
    Args:
        nakl_search: Строка для поиска в номерах накладных
        data_file: Путь к файлу с данными
        case_sensitive: Учитывать регистр при поиске
        include_shipment_date: Если True - возвращает объекты с датами, если False - только номера
    
    Returns:
        Если include_shipment_date=False: список номеров накладных
        Если include_shipment_date=True: список словарей с полями 'nakl' и 'send_date'
    """
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Файл {data_file} не найден")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка чтения JSON: {e}")
        return []
    
    # Используем словарь для уникальности по номеру накладной
    nakl_dict = {}
    
    for sheet_name, sheet_data in data.items():
        rows = sheet_data.get('rows', [])
        
        for row in rows:
            # column21 находится по индексу 20 (0-based)
            nakl_cell = row[20] if len(row) > 20 else ''
            
            if not nakl_cell or str(nakl_cell).strip() == '':
                continue
            
            nakl_str = str(nakl_cell)
            
            # Поиск с учетом или без учета регистра
            if case_sensitive:
                if nakl_search not in nakl_str:
                    continue
            else:
                if nakl_search.lower() not in nakl_str.lower():
                    continue
            
            # Если накладная уже есть в словаре, пропускаем (сохраняем первую найденную дату)
            if nakl_str in nakl_dict:
                continue
            
            # Извлекаем дату отгрузки из column25 (индекс 24)
            send_date = extract_shipment_date(row[24]) if include_shipment_date else None
            status = row[21]
            nakl_dict[nakl_str] = {
                'nakl': nakl_str,
                'send_date': send_date,
                'status': status
            }
    
    # Возвращаем в зависимости от параметра
    if include_shipment_date:
        return list(nakl_dict.values())
    else:
        return sorted(list(nakl_dict.keys()))

def find_rows_by_nakl(
    nakl_number: str,
    data_file: str = 'base_data.json',
    case_sensitive: bool = False,
    include_headers: bool = False
) -> List[Dict[str, Any]]:
    """
    Находит все строки, в которых column21 содержит указанный номер накладной.
    
    Args:
        nakl_number: Номер накладной для поиска
        data_file: Путь к файлу с данными
        case_sensitive: Учитывать регистр при поиске
        include_headers: Включить в результат заголовки и информацию о листе
    
    Returns:
        Список словарей с информацией о найденных строках
        Каждый словарь содержит:
            - 'row': список значений строки
            - 'row_index': номер строки (начиная с 2, т.к. строка 1 - заголовки)
            - 'sheet': название листа
            - 'headers': заголовки (если include_headers=True)
            - 'original_headers': оригинальные заголовки из таблицы (если include_headers=True)
    """
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Файл {data_file} не найден")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка чтения JSON: {e}")
        return []
    
    results = []
    
    for sheet_name, sheet_data in data.items():
        rows = sheet_data.get('rows', [])
        headers = sheet_data.get('headers', [])
        original_headers = sheet_data.get('original_headers', [])
        
        for row_idx, row in enumerate(rows, start=2):  # start=2, т.к. строка 1 - заголовки
            # Проверяем column21 (индекс 20)
            nakl_cell = row[20] if len(row) > 20 else ''
            
            if not nakl_cell or str(nakl_cell).strip() == '':
                continue
            
            nakl_str = str(nakl_cell)
            
            # Проверяем совпадение
            if case_sensitive:
                if nakl_number not in nakl_str:
                    continue
            else:
                if nakl_number.lower() not in nakl_str.lower():
                    continue
            
            # Формируем результат
            result = {
                'row': row,
                'row_index': row_idx,
                'sheet': sheet_name,
                'nakl_number': nakl_str
            }
            
            if include_headers:
                result['headers'] = headers
                result['original_headers'] = original_headers
            
            results.append(result)
    
    return results

def otgruzheno(
    receiver: str,
    data_file: str = 'base_data.json',
    case_sensitive: bool = False,
    exclude_delivered: bool = True,
    include_headers: bool = False
) -> List[Dict[str, Any]]:
    """
    Находит строки в листах ["Отгружено", "Контрольный диапазон", "Готовится к отгрузке"],
    где получатель (column11, индекс 10) содержит указанное значение,
    и статус доставки (column22, индекс 21) НЕ равен "Доставлен".
    
    Args:
        receiver: Имя или часть имени получателя для поиска (column11)
        data_file: Путь к файлу с данными
        case_sensitive: Учитывать регистр при поиске
        exclude_delivered: Исключать строки со статусом "Доставлен"
        include_headers: Включить в результат заголовки
    
    Returns:
        Список словарей с информацией о найденных строках
    """
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Файл {data_file} не найден")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка чтения JSON: {e}")
        return []
    
    # Листы для поиска
    target_sheets = ["Отгружено", "Контрольный диапазон", "Готовится к отгрузке"]
    
    results = []
    
    for sheet_name in target_sheets:
        if sheet_name not in data:
            print(f"⚠️ Лист '{sheet_name}' не найден в файле")
            continue
        
        sheet_data = data[sheet_name]
        rows = sheet_data.get('rows', [])
        headers = sheet_data.get('headers', [])
        original_headers = sheet_data.get('original_headers', [])
        
        for row_idx, row in enumerate(rows, start=2):  # start=2, т.к. строка 1 - заголовки
            # Проверяем column11 (индекс 10) - получатель
            receiver_cell = row[10] if len(row) > 10 else ''
            
            if not receiver_cell or str(receiver_cell).strip() == '':
                continue
            
            receiver_str = str(receiver_cell)
            
            # Проверяем совпадение с получателем
            if case_sensitive:
                if receiver not in receiver_str:
                    continue
            else:
                if receiver.lower() not in receiver_str.lower():
                    continue
            
            # Проверяем статус доставки (column22, индекс 21)
            status_cell = row[21] if len(row) > 21 else ''
            status_str = str(status_cell).strip() if status_cell else ''
            
            # Если exclude_delivered=True, исключаем строки со статусом "Доставлен"
            if exclude_delivered and status_str.lower() == "доставлен":
                continue
            
            # Формируем результат
            result = {
                'row': row,
            }
            
            if include_headers:
                result['headers'] = headers
                result['original_headers'] = original_headers
            
            results.append(result)
    
    return results

def planned(
    receiver: str,
    data_file: str = 'base_data.json',
    case_sensitive: bool = False
) -> List[Dict[str, Any]]:
    """
    Находит строки на листе "Заявки", где получатель (column11, индекс 10) содержит указанное значение.
    
    Args:
        receiver: Имя или часть имени получателя для поиска (column11)
        data_file: Путь к файлу с данными
        case_sensitive: Учитывать регистр при поиске
    
    Returns:
        Список словарей с полем 'row', содержащим строку данных
    """
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Файл {data_file} не найден")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка чтения JSON: {e}")
        return []
    
    # Проверяем, есть ли лист "Заявки"
    if "Заявки" not in data:
        print(f"⚠️ Лист 'Заявки' не найден в файле")
        return []
    
    sheet_data = data["Заявки"]
    rows = sheet_data.get('rows', [])
    
    results = []
    
    for row_idx, row in enumerate(rows, start=2):  # start=2, т.к. строка 1 - заголовки
        # Проверяем column11 (индекс 10) - получатель
        receiver_cell = row[10] if len(row) > 10 else ''
        
        if not receiver_cell or str(receiver_cell).strip() == '':
            continue
        
        receiver_str = str(receiver_cell)
        
        # Проверяем совпадение с получателем
        if case_sensitive:
            if receiver not in receiver_str:
                continue
        else:
            if receiver.lower() not in receiver_str.lower():
                continue
        
        # Добавляем только строку
        results.append({
            'row': row
        })
    
    return results

def divide_on_otpr(
    rows: List[Dict[str, Any]],
    criteria: List[int]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Делит строки на отправления по совпадению значений в указанных столбцах.
    
    Args:
        rows: Список словарей с полем 'row' (как возвращает функция planned)
        criteria: Список индексов столбцов для группировки (0-based)
    
    Returns:
        Словарь, где ключи - составные ключи группировки, значения - списки строк
        Пример:
        criteria = [21, 25, 30] - группировка по статусу доставки,
        плановой дате отгрузки и перевозчику
    """
    if not rows:
        return {}
    
    if not criteria:
        # Если критерии не указаны, все строки в одну группу
        return {'all': rows}
    
    grouped = {}
    
    for item in rows:
        row = item.get('row', [])
        
        # Формируем ключ группировки из значений указанных столбцов
        key_parts = []
        for col_idx in criteria:
            value = row[col_idx-1] if col_idx < len(row) else ''
            # Приводим к строке для создания ключа
            key_parts.append(str(value).strip())
        
        # Создаем уникальный ключ
        group_key = '|'.join(key_parts)
        
        # Если ключ пустой (все значения пустые), используем специальный ключ
        if not group_key or group_key == '|' * (len(criteria) - 1):
            group_key = 'empty_group'
        
        if group_key not in grouped:
            grouped[group_key] = []
        
        grouped[group_key].append(item)
    

    return grouped    

def cargos_by_art(cargos_string: str) -> Dict[str, Any]:
    """
    Обрабатывает строку с грузами и возвращает список проектов и сумму грузов по артикулам.
    
    Args:
        cargos_string: Строка с грузами в формате JSON (будет обернута в квадратные скобки)
    
    Returns:
        Словарь с полями:
            - 'projects': список уникальных проектов
            - 'cargos': список словарей с артикулами и суммарными количествами
            - 'total_items': общее количество позиций
    """
    # Если строка пустая или None
    if not cargos_string or str(cargos_string).strip() == '':
        return {'projects': [], 'cargos': [], 'total_items': 0}
    
    # Очищаем строку от лишних пробелов
    cargos_string = str(cargos_string).strip()
    
    # Оборачиваем в квадратные скобки, если их нет
    if not cargos_string.startswith('['):
        cargos_string = '[' + cargos_string + ']'
    
    # Парсим JSON
    try:
        cargos_list = json.loads(cargos_string)
        
        # Если это не список, пробуем обернуть еще раз
        if not isinstance(cargos_list, list):
            cargos_string = '[' + cargos_string + ']'
            cargos_list = json.loads(cargos_string)
        
        # Если все равно не список, создаем список из одного элемента
        if not isinstance(cargos_list, list):
            cargos_list = [cargos_list]
            
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        return {'projects': [], 'cargos': [], 'total_items': 0, 'error': str(e)}
    
    # Собираем все проекты и грузы
    projects = set()
    cargos_by_art = {}  # {art: count}
    
    for cargo_obj in cargos_list:
        if not isinstance(cargo_obj, dict):
            continue
        
        all_cargos = cargo_obj.get('all_cargos', [])
        
        if not all_cargos:
            continue
        
        # Если all_cargos - список проектов
        if isinstance(all_cargos, list):
            for project_data in all_cargos:
                if not isinstance(project_data, dict):
                    continue
                
                # Получаем проект
                project = project_data.get('project', '')
                if project:
                    projects.add(str(project))
                
                # Получаем грузы в проекте
                project_cargos = project_data.get('project_cargos', [])
                
                if isinstance(project_cargos, list):
                    for cargo in project_cargos:
                        if not isinstance(cargo, dict):
                            continue
                        
                        art = cargo.get('art', '')
                        count = cargo.get('count', 0)
                        
                        if art:
                            # Приводим count к int
                            try:
                                count = int(count)
                            except (ValueError, TypeError):
                                count = 0
                            
                            # Суммируем по артикулу
                            if art not in cargos_by_art:
                                cargos_by_art[art] = 0
                            cargos_by_art[art] += count
    
    # Преобразуем в список для результата
    cargos_result = [
        {'art': art, 'count': count}
        for art, count in cargos_by_art.items()
    ]
    
    # Сортируем по артикулу для удобства
    cargos_result.sort(key=lambda x: x['art'])
    
    return {
        'projects': sorted(list(projects)),
        'cargos': cargos_result,
        'total_items': len(cargos_result)
    }

def cargos_by_project(cargos_string: str) -> List[Dict[str, Any]]:
    """
    Группирует грузы по проектам из строки с грузами.
    
    Args:
        cargos_string: Строка с грузами в формате JSON (будет обернута в квадратные скобки)
    
    Returns:
        Список словарей с полями:
            - 'project': номер проекта
            - 'cargos': список словарей с артикулами и суммарными количествами для этого проекта
    
    Пример:
        >>> cargos_by_project(cargos_string)
        [
            {
                'project': '13407',
                'cargos': [
                    {'art': '81717161 Антикраж устройство Gillette Бабочка', 'count': 18},
                    {'art': '81744724 / 81749803 / 81777488 / 81717188 Бок.навеска для однораз Gill.Oral Sim', 'count': 1}
                ]
            },
            {
                'project': '13379',
                'cargos': [
                    {'art': '81683069 Бокс для кассет Gillette узкий', 'count': 9}
                ]
            }
        ]
    """
    # Если строка пустая или None
    if not cargos_string or str(cargos_string).strip() == '':
        return []
    
    # Очищаем строку и оборачиваем в квадратные скобки
    cargos_string = str(cargos_string).strip()
    if not cargos_string.startswith('['):
        cargos_string = '[' + cargos_string + ']'
    
    # Парсим JSON
    try:
        cargos_list = json.loads(cargos_string)
        if not isinstance(cargos_list, list):
            cargos_list = [cargos_list]
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        return []
    
    # Собираем грузы по проектам
    projects_dict = {}  # {project: {art: count}}
    
    for cargo_obj in cargos_list:
        if not isinstance(cargo_obj, dict):
            continue
        
        all_cargos = cargo_obj.get('all_cargos', [])
        
        if not all_cargos:
            continue
        
        if isinstance(all_cargos, list):
            for project_data in all_cargos:
                if not isinstance(project_data, dict):
                    continue
                
                # Получаем проект
                project = project_data.get('project', '')
                if not project:
                    continue
                
                project = str(project)
                
                # Инициализируем проект в словаре
                if project not in projects_dict:
                    projects_dict[project] = {}
                
                # Получаем грузы в проекте
                project_cargos = project_data.get('project_cargos', [])
                
                if isinstance(project_cargos, list):
                    for cargo in project_cargos:
                        if not isinstance(cargo, dict):
                            continue
                        
                        art = cargo.get('art', '')
                        count = cargo.get('count', 0)
                        
                        if art:
                            # Приводим count к int
                            try:
                                count = int(count)
                            except (ValueError, TypeError):
                                count = 0
                            
                            # Суммируем по артикулу в рамках проекта
                            if art not in projects_dict[project]:
                                projects_dict[project][art] = 0
                            projects_dict[project][art] += count
    
    # Преобразуем в список для результата
    result = []
    for project, cargos_dict in projects_dict.items():
        cargos_list_result = [
            {'art': art, 'count': count}
            for art, count in cargos_dict.items()
        ]
        # Сортируем по артикулу
        cargos_list_result.sort(key=lambda x: x['art'])
        
        result.append({
            'project': project,
            'cargos': cargos_list_result
        })
    
    # Сортируем по номеру проекта
    result.sort(key=lambda x: x['project'])
    
    return result


    
    

    

    
  