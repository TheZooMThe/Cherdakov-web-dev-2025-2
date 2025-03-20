n=int(input())
if 1<=n<=20:
    if n < 10:
        y = 1 * (10 ** (n - 1))
        z = 0
        o = n - 2
        for i in range(2, n + 1):
            z += i * (10 ** o)
            o -= 1
        print(y + z)
    else:
        y=123456789
        for i in range(n-9):
            y=y*100+i+10
        print(y)
            

#fix