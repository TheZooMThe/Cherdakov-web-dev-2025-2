with open("example.txt", "r", encoding='utf-8') as file:
    content = file.read()
    content+=' '
    a=''
    x=0
    max_word=[]
    for i in content:
        if i != ' ' and i.isalpha():  
            a+=i
        if content[x] == ' ' and content[x-1] == ' ':
            file.pop(x-1)
        if i == ' ':
            max_word.append(a)
            a=''
        x+=1
    b=[s for s in max_word if len(s) == len(max(max_word, key=len))]
    for i in b:
        print(i)

