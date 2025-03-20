try:
    a = int(input())
    b = int(input())
    print(a // b)
    print(a / b)
except ZeroDivisionError:
    print("Деление на ноль")
except ValueError:
    print("Некорректный ввод числа")

#добавил обработку