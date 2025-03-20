n = int(input())
# Считываем матрицу A построчно
matrix_a = [list(map(int, input().split())) for _ in range(n)]
# Считываем матрицу B построчно
matrix_b = [list(map(int, input().split())) for _ in range(n)]

# Вычисляем произведение матриц
result = [
    [
        sum(a * b for a, b in zip(row_a, col_b)) 
        for col_b in zip(*matrix_b)
    ] 
    for row_a in matrix_a
]

# Выводим результат
for row in result:
    print(" ".join(map(str, row)))