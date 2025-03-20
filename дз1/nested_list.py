n=int(input())
if 2<=n<=5:
    records=[]
    for i in range(n):
        inner_list=[]
        inner_list.append(input())
        inner_list.append((input()))
        records.append(inner_list)

    def sort_col(i):
        return i[1]
    for i in range(n):
        records[i][1]=float(records[i][1])
    records.sort(key=lambda x: x[1])
    y=records[0][1]
    x=0.0
    for i in range(n):
        if records[i][1]==y:
            x=records[i+1][1]
    
    save=[]
    for i in range(n):
        if records[i][1]==x:
            save.append(records[i][0])
    save.sort()
    for i in range(len(save)):
        print(save[i])

#fix