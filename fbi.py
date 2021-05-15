import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

headers = {
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
}
r = requests.get('https://www.fbi.gov/contact-us/field-offices/', headers=headers)
_html = r.text
soup = BeautifulSoup(_html, 'html.parser')
all_links = set(link.get('href') for link in soup.find_all('a'))
fo_links = {link.split('/')[-1]: link for link in all_links if 'contact-us/field-offices/' in link}


def get_news(fo):
    """
    :param fo: all lowercase no spaces
    :return: headline time series
    """
    fo_link = f'https://www.fbi.gov/contact-us/field-offices/{fo}/news/press-releases/'
    fo_r = requests.get(fo_link, headers=headers)
    fo_html = fo_r.text
    fo_soup = BeautifulSoup(fo_html, 'html.parser')
    # get unique query selector
    fo_query = fo_soup.find_all('button', class_='load-more')[0].get('href')
    fo_query = fo_query.split('?')[0]
    fo_news = []
    page = 1
    while True:
        fo_pg = BeautifulSoup(requests.get(fo_query + f'?page={page}', headers=headers).text, 'html.parser').find_all(
            'a')
        if not fo_pg:
            break
        fo_news = fo_news + fo_pg
        page += 1

    headlines = [hl.get_text().strip('\n') for hl in fo_news]

    return headlines


def wc(headlines):
    text = ' '.join(hl for hl in headlines)
    stopwords = set(STOPWORDS)
    stopwords.update(
        ['charge', 'charges', 'role', 'man', 'woman', 'maryland', 'virginia', 'washington', 'savannah', 'atlanta',
         'georgia', 'district', 'United States', 'conspiracy', 'member', 'involving', 'health care', 'month', 'months',
         'year', 'years', 'field', 'office', 'scheme', 'charged', 'prison', 'pleads', 'guilty',
         'defendant', 'indicted', 'federal', 'sentenced', 'former', 'fbi', 'man', 'two', 'three', 'million',
         'investigation', 'employee', 'arrest', 'officer', 'arrested', 'field office', 'convicted'])
    wordcloud = WordCloud(stopwords=stopwords, background_color='white', max_font_size=50, max_words=15,
                          min_word_length=4).generate(text)
    plt.figure()
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()


if __name__ == '__main__':
    wc(get_news('washingtondc'))
