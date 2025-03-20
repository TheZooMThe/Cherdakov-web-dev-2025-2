n=int(input())
if n>=0:
    arr=[]

    for i in range(n):
        action=input().split(' ')
        match action[0]:
            case 'insert':  #1
                arr.insert(int(action[1]),int(action[2]))
            case 'print':   #2
                print(arr)
            case 'remove':  #3
                arr.remove(int(action[1]))
            case 'append':  #4
                arr.append(int(action[1]))
            case 'sort':  #5
                arr.sort()
            case 'pop':  #6
                arr.pop(-1)
            case 'reverse':  #7
                arr.reverse()

