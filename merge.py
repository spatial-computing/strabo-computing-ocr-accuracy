import csv


if __name__ == '__main__':
    csvwrite = open('/Users/tianxiat/Documents/workspace/strabo-computing-ocr-accuracy/combine.csv', 'w')
    fieldnames = ['map_name', 'strabo_text', 'rsh_text', 'ground_truth', 'diff']
    writer = csv.DictWriter(csvwrite, fieldnames=fieldnames)
    writer.writeheader()

    log1 = open('/Users/tianxiat/Documents/workspace/strabo-computing-ocr-accuracy/Log.csv')


    reader1 = csv.reader(log1, delimiter=',', quotechar='|')


    for r in reader1:
        if r[0] == 'map_name':
            continue
        log2 = open('/Users/tianxiat/Documents/workspace/strabo-computing-ocr-accuracy/Log2.csv')
        reader2 = csv.reader(log2, delimiter=',', quotechar='|')
        for r2 in reader2:
            if r2[0] == 'map_name':
                continue
            if r[1] == r2[1] and r[0] == r2[0]:
                mn = r[0]
                st = r[2]
                rt = r2[2]
                gt = r[4]
                # print(r[5])
                c1 = int(r[-1])
                c2 = int(r2[-1])
                diff = c2 - c1

                if diff != 0:
                    print(r)
                    print(r2)
                    print("\n")

                writer.writerow({'map_name': mn, 'strabo_text': st, 'rsh_text': rt, 'ground_truth': gt, 'diff': diff})

    csvwrite.close()
