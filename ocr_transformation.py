import csv, sys
import classify_gbc


if __name__ == '__main__':
    csvwrite = open('scores.csv', 'w')
    fieldnames = ['map_name', 'org_text', 'dict_text', 'score', 'x', 'y', 'w', 'h']
    writer = csv.DictWriter(csvwrite, fieldnames=fieldnames)
    writer.writeheader()

    with open('./nw.csv') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        row_count = 0;
        try:
            for row in reader:
                row_count = row_count + 1;
                item_num = int(len(row) / 8)
                for i in range(1, item_num + 1):
                    start_sub = 8 * (i - 1)
                    if row[start_sub + 1] == '':
                        continue

                    map_name = row[start_sub+1];

                    original_alignment = row[start_sub + 2];
                    dict_alignment = row[start_sub + 3];

                    score = classify_gbc.sequence2(original_alignment, dict_alignment)

                    if score == sys.maxsize:
                        # print('Invalid alignment.')
                        pass
                    else:
                        writer.writerow({'map_name': map_name, 'org_text': original_alignment.replace(',', ''),
                                     'dict_text': dict_alignment.replace('-', '').replace(',', ''),
                                     'score':  score, 'x': row[start_sub + 4], 'y': row[start_sub + 5],
                                     'w': row[start_sub + 6], 'h': row[start_sub + 7]})
                        # pass
                        # print('score: ', score)

                print('finish row ', row_count)
        except UnicodeDecodeError:
            print(row)










