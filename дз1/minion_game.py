s = input().strip()
vowels = 'AEIOU'
kevin_score = 0
stuart_score = 0
n = len(s)

for i in range(n):
    if s[i] in vowels:
        kevin_score += n - i
    else:
        stuart_score += n - i

if kevin_score > stuart_score:
    print("Кевин", kevin_score)
elif stuart_score > kevin_score:
    print("Стёарт", stuart_score)
else:
    print("Ничья")


