from os import system
from db import airportDB
from airport import dataAirport
from utils import pause, gotoxy
from utils import about_program
import qt

db = airportDB()
airport = dataAirport()
menu = 1

while menu:
    system("cls")
    print("Главное меню")
    print("----------------------------")
    print("1. Показать таблицу")
    print("2. Добавить запись")
    print("3. Добавить несколько записей")
    print("4. Обновить запись")
    print("5. Удалить запись")
    print("6. Поиск записи")
    print("7. О программе")
    print("8. Выход")

    choice = int(input("Выберите пункт меню: "))



    system("cls")

    match choice:
        case 1:
            print("Показ таблицы")
            print("----------------------------")
            pause()
            system("cls")

            db.getData()
            pause()

            continue

        case 2:
            print("Ввод записей.")
            print("----------------------------")
            pause(); system("cls")
            db.addData(0)
            pause()
            continue

        case 3:

            print("Ввод нескольких записей." )
            print("----------------------------")
            count = int(input("Кол-во записей, который будут добавлены: "))
            system("cls")

            db.addData(count)
            pause()
            continue
            
            
        case 4:
            print("Ввод для обновления записей.")
            print("----------------------------")
            db.updateData()
            continue
            
        case 5:
            
        
            print("Удаление записи")
            print("----------------------------" )
            pause()
            system("cls")
            db.deleteData()
            pause()
            continue
            

        case 6:
            print(f"\n {"Поиск записей":8}")
            print("----------------------------" )
            pause()
            system("cls")
            db.searchData()
            pause()
            continue
            

        case 7:
            
            about_program()
            pause()
            continue
            

        case 8:
            
            system("cls")
            print("Удачи!")
            db.close_db()
            menu = 0
            continue
            

        case _:
            print("Неверный пункт меню, попробуйте ещё раз.");  pause()
            continue