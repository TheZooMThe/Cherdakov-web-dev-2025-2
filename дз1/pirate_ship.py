n=input().split()
list_items=[]
for i in range(int(n[1])):
    stuff=input().split()
    list_items.append(stuff)
for i in range(len(list_items)):
    list_items[i][1]=float(list_items[i][1])
    list_items[i][2]=float(list_items[i][2])

weight=0
ship=[]
for i in range(len(list_items)):
    list_items[i].append(round((list_items[i][2]/list_items[i][1]),2))
list_items.sort(key=lambda x: x[3])
while list_items[-1][1]+weight<int(n[0]):
    weight+=list_items[-1][1]
    ship.append(list_items[-1])
    list_items.pop(-1)
    if list_items==[]:
        break
ost=int(n[0])-weight
list_items[-1][2]=round(((list_items[-1][2]/list_items[-1][1])*ost),2)
list_items[-1][1]=ost
ship.append(list_items[-1])

ship.sort(key=lambda x: x[2], reverse=True)

for i in range(len(ship)):
    print(ship[i][0],float(ship[i][1]),float(ship[i][2]))

