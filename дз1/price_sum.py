import csv
 
with open('products.csv', 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    headers = next(csvreader)
    haight=0.0
    pencia=0.0
    small=0.0
    for row in csvreader:
        haight+= float(row[1])
        pencia+=float(row[2])
        small+=float(row[3])
    haight= round(haight, 2)
    pencia= round(pencia, 2)
    small= round(small, 2)
    print(haight, pencia, small)
    