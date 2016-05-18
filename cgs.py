import requests
from bs4 import BeautifulSoup
import argparse


def get_pop(search_word):
    print(search_word)
    r = requests.get('http://www.google.com/search',
                     params={'q': search_word,
                             "tbs":"li:1"}
                    )

    soup = BeautifulSoup(r.text, "html.parser")
    print(soup.find('div',{'id':'resultStats'}).text)
    pop_text = soup.find('div', {'id': 'resultStats'}).text

    if pop_text == '':
        return  0

    pop_text = pop_text.split(' ')[-2]
    pop_text = pop_text.replace(',', '')
    return float(pop_text)