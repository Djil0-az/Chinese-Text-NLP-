import csv#convert article from TXT to CSVmat = []with open("renmin.txt", "r",encoding='utf-8', errors='ignore') as f:    for line in f:        mat.append([l for l in line.split()])#print(mat)with open('renmin.csv', 'w',encoding='utf-8', newline='') as csvfile:    writer = csv.writer(csvfile)    for row in mat:        if len(row) != 0:            writer.writerow(row)#convert POS from txt to CSVmat2 = []with open("renminPOS.txt", "r",encoding='utf-8', errors='ignore') as f:    for line in f:        line = line[22:]        print(line)        mat2.append([l for l in line.split()])print(mat2)with open('renminPOS.csv', 'w',encoding='utf-8', newline='') as csvfile:    writer = csv.writer(csvfile)    for row in mat2:        if len(row) != 0:            writer.writerow(row)