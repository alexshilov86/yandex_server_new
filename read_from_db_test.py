import pandas as pd

# Читаем один из созданных файлов
df = pd.read_feather("Отгружено.feather")
column_39 = df.iloc[:, 36]
non_empty_cells = column_39.dropna()
if not non_empty_cells.empty:
    # .iloc[0] берет самое первое значение из оставшихся непустых
    first_value = non_empty_cells.iloc[0]
    
    # Также можно узнать, на какой строчке (индексе) оно сидит
    first_row_index = non_empty_cells.index[0]
    
    print(f"Имя 40-го столбца в таблице: '{column_39.name}'")
    print(f"Первая непустая ячейка находится на строке: {first_row_index}")
    print(f"Значение в этой ячейке: {first_value}")
else:
    print("В 40-м столбце вообще нет заполненных ячеек (он полностью пустой).")