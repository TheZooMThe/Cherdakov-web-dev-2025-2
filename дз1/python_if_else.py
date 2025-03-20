x = int(input())
if 1<=x<=100:
    if x%2==0:
        if 2<=x<=5:
            print("Not Weird")
        elif 6<=x<=20:
            print("Weird")
        elif 20<=x:
            print("Not Weird")
    else:
        print("Weird")

