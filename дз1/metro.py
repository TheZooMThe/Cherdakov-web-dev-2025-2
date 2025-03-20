n=int(input())
p=0
metro=[]
for i in range(n):
    pas=input().split(' ')
    metro.append(pas)
T=int(input())
for i in metro:
    if int(i[0]) <= T and T<= int(i[1]):
        p+=1
print(p)
