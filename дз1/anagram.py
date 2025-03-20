str1=input()
str2=input()
if len(str1)==len(str2):
    dict1={}
    dict2={}

    for i in str1:
        n=0
        for j in range(len(str1)):
            if str1[j]==i:
                n+=1
        
        dict1.update({i:n})
    for i in str2:
        n=0
        for j in range(len(str2)):
            if str2[j]==i:
                n+=1
        
        dict2.update({i:n})
    flag=0
    for key1, value1 in dict1.items():
        for key2, value2 in dict2.items():
            if key1==key2 and value1==value2:
                flag+=1
                break
    if flag==len(dict1):
        print("Yes")
    else:
        print("No")
else:
    print("No")