# тестирование всевозможных функций для работы с базой
from base_functions import otgruzheno, divide_on_otpr, cargos_by_project, find_nakl_numbers, find_rows_by_nakl, planned, cargos_by_art, extract_shipment_date

nakl_last = "6078" # 10213398851
nakl_full = "26-03681086044"
reciver = "Безделева Анастасия Дмитриевна"

# ============= ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ =============
if __name__ == "__main__":

    print ("тестирование списка накладных по частичной накладной " + nakl_last)
    nakl_list = find_nakl_numbers(nakl_last)
    print (f"Найденно {len(nakl_list)} накладных")
    for nakl_info in nakl_list:
        print (nakl_info)

    print("-" * 60)
    print (f"Тестирование нахождения полной накладной {nakl_full}")
    nakl_info = find_rows_by_nakl(nakl_full)
    print (f"Найденно {len(nakl_info)} строк(а) в базе")
    for row in nakl_info:
        print (row['row'])

    print("-" * 60)

    print (f"Тестирование отгруженных на получателя {reciver}")
    criteria = [5, 21, 25, 30]
    nakl_list = otgruzheno(reciver) # строки с отправлениями на получателя, еще не доставленные
    otpravlenia = divide_on_otpr(nakl_list, criteria) # разделение строк на отправления
    print (f"Найденной {len(otpravlenia)} отправлений на получателя {reciver}")
    for otpr in otpravlenia:
        for gruz in otpravlenia[otpr]:
            print (f"Отгруженно {extract_shipment_date(gruz['row'][24])}")
    print("-" * 60)
    
    reciver ="Крачковский Антон Александрович"
    print (f"Тестирование запланированных на получателя {reciver}")
    nakl_list = planned(reciver)
    print (f"Найденно {len(nakl_list)} отправлений на получателя {reciver}")
    for otpr in nakl_list:
        print (f"Проект {otpr['row'][2]}. План. дата отгрузки {extract_shipment_date(otpr['row'][25])}")
    print("-" * 60)

    reciver = "Безделева Анастасия Дмитриевна"
    print (f"Тестирование списка отправленных грузок на получателя {reciver}")
    reciver = "Безделева Анастасия Дмитриевна"
    criteria = [5, 21, 25, 30]
    nakl_list = otgruzheno(reciver) # строки с отправлениями на получателя, еще не доставленные
    otpravlenia = divide_on_otpr(nakl_list, criteria) # разделение строк на отправления
    print (f"Найденной {len(otpravlenia)} отправлений на получателя {reciver}")
    
    for otpr in otpravlenia:
        cargos_str = []
        send_date = extract_shipment_date(otpravlenia[otpr][0]['row'][24])
        reciver_city = otpravlenia[otpr][0]['row'][8]
        for gruz in otpravlenia[otpr]:
            cargos_str.append(gruz['row'][38])
        cargo_in_otpr_json = cargos_by_art(",".join(cargos_str))
        print (f"Город назначения: {reciver_city}")
        print (f"Дата отгрузки: {send_date}")
        print (f"Проекты: {' - '.join(cargo_in_otpr_json['projects'])}")
        for art in cargo_in_otpr_json['cargos']:
            print (f"{art['art']} - {art['count']} шт")
        print("-" * 30)
    # print("-" * 60)
    # 
    # 
    # 


    
    # print (cargos_str)
    # print (cargos_by_project(",".join(cargos_str)))

    # # cargos_by_project