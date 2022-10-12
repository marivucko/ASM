import pandas as pd
from enum import Enum
from scipy.stats import pearsonr
import seaborn as sns
from matplotlib import pyplot
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.common.by import By
from tabulate import tabulate
import numpy as np
import os
from scipy import stats


class Type(Enum):
    SUBMISSION = 'submission'
    COMMENT = 'comment'


OUTPUT_DATA_CLEANED_SUBMISSIONS_PATH = '../../results/output_data_cleaned/submissions.csv'
OUTPUT_DATA_CLEANED_COMMENTS_PATH = '../../results/output_data_cleaned/comments.csv'
submissions = pd.DataFrame()
comments = pd.DataFrame()
PATH = "C:\Program Files (x86)\chromedriver_win32\chromedriver_win32 (2)\chromedriver.exe"
options = Options()
options.add_argument('--no-sandbox')


def get_element_by_xpath(driver, xpath):
    try:
        return driver.find_element(By.XPATH, xpath).text
    except NoSuchElementException:
        return ''


def get_elements_by_xpath(driver, xpath):
    try:
        elements = driver.find_elements(By.XPATH, xpath)
        text = ''
        for element in elements:
            text = text + element.text + "\n"
        return text
    except NoSuchElementException:
        return ''


def get_elements_by_xpath_and_return_first_few(driver, xpath):
    try:
        elements = driver.find_elements(By.XPATH, xpath)
        text = ''
        i = 0
        while (i < 6) and (i < len(elements)):
            text = text + elements[i].text + "\n"
            i = i + 1
        return text
    except NoSuchElementException:
        return ''


def check_if_ids_are_unique_and_not_empty(data, name_of_data_frame):
    ids_are_unique = data['id'].is_unique
    ids_are_not_empty_string = not data[data['id'] == ''].values.any()
    print(f'Ids are unique in {name_of_data_frame}:', ids_are_unique)
    print(f'Ids are not empty strings in {name_of_data_frame}:', ids_are_not_empty_string)


def read_submissions_or_comments_from_csv(t):
    global submissions, comments
    data = []
    for i in range(0, 12):
        data.append(pd.read_csv(f'../../input_data/reddit2008/{t.value}s_2008_asm/csv-{i}.csv', low_memory=False, index_col=0, header=0))
    if t == Type.SUBMISSION:
        submissions = pd.concat(data, axis=0, ignore_index=True)
        submissions = submissions.loc[:, ['id', 'url', 'permalink', 'author', 'created_utc', 'subreddit', 'subreddit_id', 'num_comments', 'over_18']]
        check_if_ids_are_unique_and_not_empty(submissions, t.value + 's')
        submissions.to_csv(OUTPUT_DATA_CLEANED_SUBMISSIONS_PATH, encoding='utf-8')
        return submissions
    elif t == Type.COMMENT:
        comments = pd.concat(data, axis=0, ignore_index=True)
        comments = comments.loc[:, ['id', 'author', 'link_id', 'parent_id', 'created_utc', 'subreddit', 'subreddit_id']]
        check_if_ids_are_unique_and_not_empty(comments, t.value + 's')
        comments.to_csv(OUTPUT_DATA_CLEANED_COMMENTS_PATH, encoding='utf-8')
        return comments


def read_submissions_and_comments():
    global submissions, comments
    if submissions.empty or comments.empty:
        if os.path.isfile(OUTPUT_DATA_CLEANED_SUBMISSIONS_PATH):
            submissions = pd.read_csv(OUTPUT_DATA_CLEANED_SUBMISSIONS_PATH, low_memory=False, index_col=0, header=0)
        else:
            submissions = read_submissions_or_comments_from_csv(Type.SUBMISSION)
        if os.path.isfile(OUTPUT_DATA_CLEANED_COMMENTS_PATH):
            comments = pd.read_csv(OUTPUT_DATA_CLEANED_COMMENTS_PATH, low_memory=False, index_col=0, header=0)
        else:
            comments = read_submissions_or_comments_from_csv(Type.COMMENT)
    return submissions, comments


def _top_10_most_active_users_on_reddit_com():              # koristi se za pitanje 18 u UserNet
    read_submissions_and_comments()
    submissions_important_columns = submissions.loc[:, ['id', 'subreddit', 'subreddit_id', 'author']]
    comments_important_columns = comments.loc[:, ['id', 'subreddit', 'subreddit_id', 'author']]
    result = pd.concat([submissions_important_columns, comments_important_columns])
    result = result[result['author'] != '[deleted]']
    authors_with_large_num_of_submissions = result[result['subreddit'] == 'reddit.com'].groupby(['author'])['id'].agg('nunique').reset_index().nlargest(10, 'id')
    print('10 korisnika koji su bili najaktivniji na sabreditu reddit.com:')
    print(tabulate(authors_with_large_num_of_submissions, headers=['Korisnik', 'Broj aktivnosti'], tablefmt='psql', showindex="never", numalign='center', stralign='center'))


def _1a():
    read_submissions_and_comments()
    submissions_subreddit_id = submissions.loc[:, ['subreddit_id']]
    comments_subreddit_id = comments.loc[:, ['subreddit_id']]
    subreddit_id = pd.concat([submissions_subreddit_id, comments_subreddit_id])
    unique_subreddit_id = subreddit_id['subreddit_id'].nunique()
    print(f'Različitih sabredita koji se pojavljuju u posmatranom periodu ima {unique_subreddit_id}.')


def _1b():
    read_submissions_and_comments()
    submissions_num_of_users = submissions.loc[:, ['subreddit', 'subreddit_id', 'author']]
    comments_num_of_users = comments.loc[:, ['subreddit', 'subreddit_id', 'author']]
    sub_and_comment_num_of_users = pd.concat([submissions_num_of_users, comments_num_of_users])
    sub_and_comment_num_of_users = sub_and_comment_num_of_users[sub_and_comment_num_of_users['author'] != '[deleted]'].groupby(['subreddit', 'subreddit_id'])['author'].agg('nunique').reset_index().nlargest(10, 'author')
    print('Sabrediti najvažniji po broju korisnika su:')
    print(tabulate(sub_and_comment_num_of_users, headers=['Subreddit', 'Subreddit id', 'Broj korisnika'], tablefmt='psql', showindex="never", numalign='center', stralign='center'))


def _1c():
    read_submissions_and_comments()
    comments_in_subreddits = comments.groupby(['subreddit', 'subreddit_id'])['id'].agg([('Number of comments per subreddit', pd.Series.nunique)]).nlargest(10, 'Number of comments per subreddit').reset_index()
    print('Sabrediti najvažniji po broju komentara su:')
    print(tabulate(comments_in_subreddits, headers=['Subreddit', 'Subreddit id', 'Broj komentara'], tablefmt='psql', showindex="never", numalign='center', stralign='center'))


def _1c_():
    read_submissions_and_comments()
    comments_in_subreddits = submissions.groupby(['subreddit', 'subreddit_id'])['num_comments'].agg([('Number of comments per subreddit', np.sum)]).nlargest(10, 'Number of comments per subreddit').reset_index()
    print('Sabrediti najvažniji po broju komentara su:')
    print(tabulate(comments_in_subreddits, headers=['Subreddit', 'Subreddit id', 'Broj komentara'], tablefmt='psql', showindex="never", numalign='center', stralign='center'))


def _1():
    _1a()
    _1b()
    _1c()


def _2():
    read_submissions_and_comments()
    submissions_important_columns = submissions.loc[:, ['subreddit', 'subreddit_id', 'author']]
    comments_important_columns = comments.loc[:, ['subreddit', 'subreddit_id', 'author']]
    group = pd.concat([submissions_important_columns, comments_important_columns])
    num_of_subreddits = group['subreddit_id'].nunique()
    num_of_authors = group['author'].loc[group['author'] != '[deleted]'].nunique()
    print(f'Prosečan broj zabeleženih korisnika aktivnih u posmatranom periodu po sabreditu je {num_of_authors} / {num_of_subreddits} = {round(num_of_authors / num_of_subreddits, 2)}.')


def _3():
    read_submissions_and_comments()
    submissions_important_columns = submissions.loc[:, ['id', 'author']]
    comments_important_columns = comments.loc[:, ['id', 'author']]
    authors_with_large_num_of_submissions = submissions_important_columns[submissions_important_columns['author'] != '[deleted]'].groupby(['author'])['id'].agg('nunique').reset_index().nlargest(10, 'id')
    authors_with_large_num_of_comments = comments_important_columns[comments_important_columns['author'] != '[deleted]'].groupby(['author'])['id'].agg('nunique').reset_index().nlargest(10, 'id')
    print('10 korisnika sa najvećem brojem objava:')
    print(tabulate(authors_with_large_num_of_submissions, headers=['Korisnik', 'Broj obajva'], tablefmt='psql', showindex="never", numalign='center', stralign='center'))
    print('10 korisnika sa najvećem brojem komentara:')
    print(tabulate(authors_with_large_num_of_comments, headers=['Korisnik', 'Broj komentara'], tablefmt='psql', showindex="never", numalign='center', stralign='center'))


def _4():
    read_submissions_and_comments()
    submissions_important_columns = submissions.loc[:, ['subreddit', 'subreddit_id', 'author']]
    comments_important_columns = comments.loc[:, ['subreddit', 'subreddit_id', 'author']]
    result = pd.concat([submissions_important_columns, comments_important_columns])
    result = result[result['author'] != '[deleted]'].groupby(['author'])['subreddit_id'].agg('nunique').reset_index().nlargest(10, 'subreddit_id')
    print('10 korisnika koji su aktivni na najvećem broju sabredita:')
    print(tabulate(result, headers=['Korisnik', 'Broj sabredita na kojima je aktivan'], tablefmt='psql', showindex="never", numalign='center', stralign='center'))


NUMBER_OF_SUBMISSIONS_TEXT = "Korisnikov broj obajva"
NUMBER_OF_COMMENTS_TEXT = "Korisnikov broj komentara"


def _5():
    read_submissions_and_comments()
    submissions_important_columns = submissions.loc[:, ['subreddit', 'subreddit_id', 'author', 'id']]
    comments_important_columns = comments.loc[:, ['subreddit', 'subreddit_id', 'author', 'id']]
    submissions_important_columns = submissions_important_columns[submissions_important_columns['author'] != '[deleted]'].groupby(['author'])['id'].agg('nunique').reset_index().rename(columns={'id': NUMBER_OF_SUBMISSIONS_TEXT})
    comments_important_columns = comments_important_columns[comments_important_columns['author'] != '[deleted]'].groupby(['author'])['id'].agg('nunique').reset_index().rename(columns={'id': NUMBER_OF_COMMENTS_TEXT})
    union = pd.merge(submissions_important_columns, comments_important_columns, on='author', how='outer').fillna(0)
    print(f'Pirsonov koeficijent korelacije je (r, p) = {pearsonr(union[NUMBER_OF_SUBMISSIONS_TEXT], union[NUMBER_OF_COMMENTS_TEXT])}, odnosno matrica korelacije je: ')
    print(union.corr(method='pearson'))
    # show graph of number of user's submissions and comments
    sns.scatterplot(x=NUMBER_OF_SUBMISSIONS_TEXT, y=NUMBER_OF_COMMENTS_TEXT, data=union)
    pyplot.scatter(union[NUMBER_OF_SUBMISSIONS_TEXT], union[NUMBER_OF_COMMENTS_TEXT], color="blue")
    pyplot.savefig(f'../results/statistical_analysis/linear_correlation.jpg')
    pyplot.show()
    # show linear regression of number of user's submissions and comments
    x = union[NUMBER_OF_SUBMISSIONS_TEXT]
    y = union[NUMBER_OF_COMMENTS_TEXT]
    gradient, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    mn = np.min(x)
    mx = np.max(x)
    x1 = np.linspace(mn, mx, 500)
    y1 = gradient * x1 + intercept
    pyplot.xlabel(NUMBER_OF_SUBMISSIONS_TEXT)
    pyplot.ylabel(NUMBER_OF_COMMENTS_TEXT)
    pyplot.plot(x, y, 'ob')
    pyplot.plot(x1, y1, '-r')
    pyplot.savefig(f'../results/statistical_analysis/linear_regression.jpg')
    pyplot.show()


def _6():
    read_submissions_and_comments()
    a = submissions.nlargest(10, 'num_comments').fillna('').reset_index()
    s = Service(PATH)
    op = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=s, options=op)
    driver.set_page_load_timeout(30)
    print("10 objava koje poseduju najveći broj komentara, subrediti na kojima su postavljene i redom njihov sadržaj za one kod kojih je fleg over_18 postavljen na false: ")
    print(tabulate(a.loc[:, ['id', 'subreddit', 'num_comments', 'over_18']], headers=['id of submission', 'subreddit', 'num_comments', 'over_18'], tablefmt='psql', showindex="never", numalign='center', stralign='center'))
    # print(tabulate(a.loc[:, ['id', 'subreddit', 'subreddit_id', 'num_comments', 'author', 'url', 'permalink', 'over_18']], headers=['id', 'subreddit', 'subreddit_id', 'num_comments', 'author', 'url', 'permalink', 'over_18'], tablefmt='psql', showindex="never", numalign='center', stralign='center'))
    for i in range(0, 10):
        time.sleep(0.5)
        row = a.iloc[[i], 1:]
        if row['over_18'].to_string(index=False) == 'False':
            try:
                print(
                    f'{i + 1}. id of submission: {row["id"].values[0]}, name of subreddit: {row["subreddit"].values[0]}')
                driver.get(a.iloc[i]['url'])
                print('-' * 100)
                if a.iloc[i]['permalink'] in a.iloc[i]['url']:
                    print(get_element_by_xpath(driver, "//div[contains(@class, '_2SdHzo12ISmrC8H86TgSCp _29WrubtjAcKqzJSPdQqQ4h')]"))
                else:
                    print(get_elements_by_xpath(driver, "//h1"))
                    print(get_elements_by_xpath_and_return_first_few(driver, "//p"))
                print('\n')
            except WebDriverException as e:
                print('Error', e)
    driver.close()
    driver.quit()


def statistical_analysis():
    _1()
    _2()
    _3()
    _4()
    _5()
    _6()


# statistical_analysis()