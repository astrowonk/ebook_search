from bs4 import BeautifulSoup
import requests
import pandas as pd
from collections import Counter


def extract_urls(x):
    soup = BeautifulSoup(x.content, 'html.parser')
    return [x.get('href') for x in soup.find_all('a') if x.find('source')]


def extract_data_from_book_page(x):
    soup = BeautifulSoup(x.content, 'html.parser')
    file_url = [
        x.get('href') for x in soup.find_all('a')
        if x.get('href').endswith('azw3')
    ][0]
    author = [
        x.text for x in soup.find_all('span')
        if x.get("property") == 'schema:name'
    ][0]
    title = [
        x.text for x in soup.find_all('h1')
        if x.get("property") == 'schema:name'
    ][0]
    return author, title, file_url


def myfmt(x):
    if len(x) == 1:
        return x + "."
    return x


def process_url_to_data(x):

    list_form = [y for y in x.split('/') if y and y]
    #print(list_form)
    if len(list_form) > 3:
        list_form = list_form[:-1]
    #print(x,list_form)
    _, author_raw, title_raw = list_form
    parsed_author = [x.title() for x in author_raw.split('-')]
    last_name = parsed_author[-1]
    #print(parsed_author[:-1])
    first_plus = " ".join([myfmt(x) for x in parsed_author[:-1]])
    title = title_raw.replace("-", " ").title()
    book_url = x + '/downloads/' + x.replace('/ebooks/', '').replace(
        '/', '_') + '.azw3'
    search_string = ' '.join([title, last_name, first_plus])
    return {
        'title': title,
        'author_last': last_name,
        'author_first': first_plus,
        'title_HREF': f"https://standardebooks.org{book_url}",
        'search_block': search_string
    }


class ebookData():
    def __init__(self) -> None:
        url_list = pd.read_csv('url_list.csv')['url'].tolist()
        self.df = pd.DataFrame([process_url_to_data(x) for x in url_list])

    @staticmethod
    def search_score(clean_text, search):
        """Not so great method stolen from another project"""
        word_list = [
            x for x in clean_text.lower().split(' ') if x not in [
                'the', 'and', 'if', 'with', 'of', 'no', 'is', 'by', 'from',
                'other', 'than'
            ]
        ]
        counter_dict = {
            key: val
            for key, val in Counter(word_list).most_common() if key
        }
        search_terms = search.lower().split()
        return sum([counter_dict.get(x, -2) for x in search_terms])

    def search(self, search):
        search = search.lower()
        return_cols = ['title', 'author_last', 'author_first','title_HREF']
        df = self.df.copy()
        if not search:
            return pd.DataFrame(columns=return_cols)
        df['search_score'] = df['search_block'].apply(self.search_score,
                                                      args=(search, ))
        return df.query('search_score > 0').sort_values(
            'search_score', ascending=False)[return_cols]
