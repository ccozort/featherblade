import csv

with open("data.csv", 'r') as d:
    exampleFile = d
    exampleReader = csv.reader(d)
    exampleData = list(exampleReader)
    print(exampleData)