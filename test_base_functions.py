# тестирование всевозможных функций для работы с базой
from base_functions import otgruzheno, divide_on_otpr, cargos_by_project, find_nakl_numbers, find_rows_by_nakl, planned, cargos_by_art

nakl_last = "98851" # 10213398851
nakl_full = "26-10531005889"
reciver = "Безделева Анастасия Дмитриевна"

# ============= ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ =============
if __name__ == "__main__":

    
    print("-" * 60)
    criteria = [5, 21, 25, 30]
    nakl_list = otgruzheno("Безделева Анастасия Дмитриевна")
    otpravlenia = divide_on_otpr(nakl_list, criteria)

    cargos_str = []
    for otpr in otpravlenia:
        for gruz in otpravlenia[otpr]:
            cargos_str.append(gruz['row'][38])
    
    print (cargos_str)
    print (cargos_by_project(",".join(cargos_str)))

    # cargos_by_project