__author__ = 'rmenon'

import sys
from sklearn.externals import joblib
import numpy
import csv, re

model = joblib.load('./gbc_model/gbc_model.pkl')
vec = joblib.load('./gbc_model/vectorizer.pkl')
lb = joblib.load('./gbc_model/binarizer.pkl')

def gbc(prevChar, currentChar, nextChar, label):
    X = numpy.array([[prevChar, currentChar, nextChar]])
    feature_dict = [dict(enumerate(x)) for x in X.tolist()]
    vectorized_X = vec.transform(feature_dict).toarray()
    binarized_label = lb.transform(numpy.array([[label]]))
    return model.score(vectorized_X, binarized_label)
 
def char_match(strg, search=re.compile(r'[^a-z-]').search):
    return not bool(search(strg))

def find_score():
    with open('python_input.csv', 'r', newline='') as fp:
        reader = csv.reader(fp)
        for row in reader:
            ##vals = row.split(',')
            truth = row[0].lower()
            dict = row[1].lower()
            sequence(truth, dict)

	
def sequence(truth, dict):
    if not char_match(truth) or not char_match(dict):
        return

    list_truth  = list(truth)
    list_dict = list(dict)
    score = 0
    for j, d in enumerate(list_dict):
        if len(list_truth) == len(list_dict):
            t = list_truth[j]
        else:
            print(list_truth)
            print(list_dict)
            return
        label = '"' + t + '"'
        currentChar = '"' + d + '"'

        if j==0:
            prevChar = '"SS"'
        else:
            prevChar = '"' + list_dict[j-1] + '"'

        if j==len(list_dict)-1:
            nextChar = '"ES"'
        else:
            nextChar = '"' + list_dict[j+1] + '"'
	
        score  = score + gbc(prevChar, currentChar, nextChar, label)  

    normalized_score = score/(j+1)
    with open('python_result.csv', 'a', newline='') as fp:
        a = csv.writer(fp, delimiter=',')
        data = [[truth, dict, str(normalized_score)]]
        a.writerows(data)


def sequence2(truth, dict):
    # if not char_match(truth) or not char_match(dict):
    #     return
    list_truth  = list(truth)
    list_dict = list(dict)
    score = 0
    j = 0
    for j, d in enumerate(list_dict):
        if len(list_truth) == len(list_dict):
            t = list_truth[j]
        else:
            # print(list_truth)
            # print(list_dict)
            return sys.maxsize
        label = t
        currentChar = d

        if j==0:
            prevChar = 'SS'
        else:
            prevChar = list_dict[j-1]

        if j==len(list_dict)-1:
            nextChar = 'ES'
        else:
            nextChar = list_dict[j+1]

        score  = score + gbc(prevChar, currentChar, nextChar, label)

    normalized_score = score/(j+1)
    return normalized_score