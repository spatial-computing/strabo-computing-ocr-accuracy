import urllib3, csv


def verifyWord(word):
    http = urllib3.PoolManager()
    r = http.request('GET', 'http://www.dictionary.com/browse/' + word + '?s=t')
    response = r.data.decode('utf-8').lower()

    if response.find('there are no results for:') != -1 or response.find('did you mean') != -1 or response.find('there\'s not a match') != -1:
        return False
    else:
        return True


if __name__ == '__main__':
    # Read in the top score candidates.
    csvfile = open('top_scores.csv', 'r')
    result_file = open('top_scores_valid.csv', 'w')

    rows = csv.reader(csvfile, delimiter=',', quotechar='|')
    writer = csv.writer(result_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for r in rows:
        if r[0] == 'map':
            r.append('valid')
        else:
            word = r[2]
            result = verifyWord(word)
            r.append(str(result))
            print('word: %s, valid: %s' % (word, result))
        writer.writerow(r)

    csvfile.close()
    result_file.close()