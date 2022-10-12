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
import csv
import mysql.connector as mysql


class Type(Enum):
    SUBMISSION = 'submission'
    COMMENT = 'comment'


DATABASE_NAME = 'ASM_baza'
TABLE_NAME_SUBMISSIONS = 'Submissions'
TABLE_NAME_COMMENTS = 'Comments'

submissions = pd.DataFrame()
comments = pd.DataFrame()
PATH = "C:\Program Files (x86)\chromedriver_win32\chromedriver_win32 (2)\chromedriver.exe"
options = Options()
options.add_argument('--no-sandbox')


db = mysql.connect(
        host="localhost",
        user="root",
        password="123#Madmin",
        database=DATABASE_NAME,
    )
cursor = db.cursor()


def create_database():
    global db, cursor
    db = mysql.connect(
        host="localhost",
        user="root",
        password="123#Madmin",
        database=DATABASE_NAME,
    )
    cursor = db.cursor()
    cursor.execute("DROP DATABASE IF EXISTS " + DATABASE_NAME)
    cursor.execute("CREATE DATABASE " + DATABASE_NAME)
    cursor.execute("USE " + DATABASE_NAME)
    cursor.execute(
        "CREATE TABLE " + TABLE_NAME_SUBMISSIONS + "(" +
        "id VARCHAR(255) NOT NULL PRIMARY KEY, "
        # "url TEXT, "
        # "permalink VARCHAR(255), "
        "author VARCHAR(255), "
        # "created_utc INT, "
        "subreddit VARCHAR(255), "
        "subreddit_id VARCHAR(255), "
        "num_comments INT "
        # ,
        # "score INT, "
        # "over_18 BOOL, "
        # "distinguished VARCHAR(255), "
        # "domain VARCHAR(255), "
        # "stickied BOOL, "
        # "locked BOOL, "
        # "hide_score BOOL "
        ")"
    )
    cursor.execute(
        "CREATE TABLE " + TABLE_NAME_COMMENTS + "(" +
        "id VARCHAR(255) NOT NULL PRIMARY KEY, "
        # "url TEXT, "
        "parent_id VARCHAR(255), "
        "author VARCHAR(255), "
        # "created_utc INT, "
        "subreddit VARCHAR(255), "
        "subreddit_id VARCHAR(255) "
        # ,
        # "score INT, "
        # "over_18 BOOL, "
        # "distinguished VARCHAR(255), "
        # "domain VARCHAR(255), "
        # "stickied BOOL, "
        # "locked BOOL, "
        # "hide_score BOOL "
        ")"
    )
    cursor.execute("USE " + DATABASE_NAME)


def read_submissions_or_comments_from_csv(t):
    global submissions, comments
    data = []
    for i in range(0, 2):
        data.append(pd.read_csv(f'../../input_data/reddit2008/{t.value}s_2008_asm/csv-{i}.csv', low_memory=False, index_col=0, header=0))
    if t == Type.SUBMISSION:
        submissions = pd.concat(data, axis=0, ignore_index=True)
        for index, row in submissions.iterrows():
            s = f"INSERT INTO { TABLE_NAME_SUBMISSIONS } (id, author, subreddit, subreddit_id, num_comments) VALUES " \
                f"('{ row['id'] }' , '{ row['author'] }', '{ row['subreddit'] }', '{ row['subreddit_id'] }', '{ row['num_comments']}')"
            cursor.execute(s)
            db.commit()
    elif t == Type.COMMENT:
        comments = pd.concat(data, axis=0, ignore_index=True)
        for index, row in comments.iterrows():
            s = f"INSERT INTO {TABLE_NAME_COMMENTS} (id, parent_id, author, subreddit, subreddit_id) VALUES " \
                f"('{row['id']}' , '{row['parent_id']}', '{row['author']}', '{row['subreddit']}', '{row['subreddit_id']}')"
            cursor.execute(s)
            db.commit()


def fill_submissions_and_comments():
    global submissions, comments
    if submissions.empty or comments.empty:
        create_database()
        read_submissions_or_comments_from_csv(Type.SUBMISSION)
        read_submissions_or_comments_from_csv(Type.COMMENT)


def _1a():
    fill_submissions_and_comments()
    submissions_subreddit_id = submissions.loc[:, ['subreddit_id']]
    comments_subreddit_id = comments.loc[:, ['subreddit_id']]
    subreddit_id = pd.concat([submissions_subreddit_id, comments_subreddit_id])
    unique_subreddit_id = pd.unique(subreddit_id['subreddit_id'])
    print(f'Različitih sabredita koji se pojavljuju u posmatranom periodu ima { len(unique_subreddit_id) }.')


def _1b():
    fill_submissions_and_comments()
    submissions_num_of_users = submissions.loc[:, ['subreddit', 'subreddit_id', 'author']]
    comments_num_of_users = comments.loc[:, ['subreddit', 'subreddit_id', 'author']]
    sub_and_comment_num_of_users = pd.concat([submissions_num_of_users, comments_num_of_users])
    sub_and_comment_num_of_users = sub_and_comment_num_of_users[sub_and_comment_num_of_users['author'] != '[deleted]'].groupby(['subreddit', 'subreddit_id'])['author'].agg(
        'nunique').reset_index().nlargest(10, 'author')
    print('Sabrediti najvažniji po broju korisnika su:')
    print(tabulate(sub_and_comment_num_of_users, headers=['Subreddit', 'Subreddit id', 'Broj korisnika'], tablefmt='psql', showindex="never", numalign='center', stralign='center'))


def _1c():
    fill_submissions_and_comments()
    comments_in_subreddits = submissions.groupby(['subreddit', 'subreddit_id'])['num_comments'].agg([('Number of comments per subreddit', np.sum)]).nlargest(100, 'Number of comments per subreddit').reset_index()
    print('Sabrediti najvažniji po broju komentara su:')
    print(tabulate(comments_in_subreddits, headers=['Subreddit', 'Subreddit id', 'Broj komentara'], tablefmt='psql', showindex="never", numalign='center', stralign='center'))

    comments_in_subreddit1 = comments.groupby(['subreddit', 'subreddit_id'])['id'].agg([('Number of comments per subreddit', 'nunique')]).nlargest(100, 'Number of comments per subreddit').reset_index()
    print(tabulate(comments_in_subreddit1, headers=['Subreddit', 'Subreddit id', 'Broj komentara'], tablefmt='psql', showindex="never", numalign='center', stralign='center'))


def _1():
    _1a()
    _1b()
    _1c()


def _2():
    num_of_subreddit = submissions['subreddit_id'].nunique() + comments['subreddit_id'].nunique()
    grupisano1 = submissions.loc[:, ['subreddit', 'subreddit_id', 'author']]
    grupisano2 = comments.loc[:, ['subreddit', 'subreddit_id', 'author']]
    gr = pd.concat([grupisano1, grupisano2])
    num_of_authors = gr['author'].nunique()
    print('num_of_subreddit', num_of_subreddit)
    print('num_of_authors', num_of_authors)
    print('number of authors per subreddit', num_of_authors / num_of_subreddit)


def _3():
    print('---3---')
    grupisano1 = submissions.loc[:, ['subreddit', 'subreddit_id', 'author']]
    grupisano2 = comments.loc[:, ['subreddit', 'subreddit_id', 'author']]
    grupisano1 = grupisano1[grupisano1['author'] != '[deleted]'].groupby(['author'])['subreddit_id'].agg('nunique').reset_index().nlargest(10, 'subreddit_id')
    grupisano2 = grupisano2[grupisano2['author'] != '[deleted]'].groupby(['author'])['subreddit_id'].agg('nunique').reset_index().nlargest(10, 'subreddit_id')
    print('a3\n', grupisano1.rename(columns={'subreddit_id': 'Number of submissions by author'}).to_string(index=False))
    print('a1\n', grupisano2.rename(columns={'subreddit_id': 'Number of comments by author'}).to_string(index=False))


def _4():
    print('---4---')
    grupisano1 = submissions.loc[:, ['subreddit', 'subreddit_id', 'author']]
    grupisano2 = comments.loc[:, ['subreddit', 'subreddit_id', 'author']]
    gr = pd.concat([grupisano1, grupisano2])
    gr = gr[gr['author'] != '[deleted]'].groupby(['author'])['subreddit_id'].agg('nunique').reset_index().nlargest(10, 'subreddit_id')
    print('a3\n', gr.rename(columns={'subreddit_id': 'Number of subreddits on which the author is active'}).to_string(index=False))


def _5():
    print('---5---')
    grupisano1 = submissions.loc[:, ['subreddit', 'subreddit_id', 'author']]
    grupisano2 = comments.loc[:, ['subreddit', 'subreddit_id', 'author']]
    grupisano1 = grupisano1[grupisano1['author'] != '[deleted]'].groupby(['author'])['subreddit_id'].agg(
        'nunique').reset_index().rename(columns={'subreddit_id': 'Submissions'})
    grupisano2 = grupisano2[grupisano2['author'] != '[deleted]'].groupby(['author'])['subreddit_id'].agg(
        'nunique').reset_index().rename(columns={'subreddit_id': 'Comments'})
    gr = pd.merge(grupisano1, grupisano2, on='author', how='outer').fillna(0)
    gr['more'] = gr['Submissions'] + gr['Comments'] #pearsonr(gr['Submissions'], gr['Comments'])
    print('a3\n', gr)
    print(pearsonr(gr['Submissions'], gr['Comments']))
    print(gr.corr(method='pearson'))
    sns.scatterplot(x="Submissions", y="Comments", data=gr)
    pyplot.scatter(gr['Submissions'], gr['Comments'])
    pyplot.show()


def statistical_analysis():
    _1b()
    _2()
    _3()
    _4()
    _5()


# _1c()
read_submissions_or_comments_from_csv(Type.COMMENT)
#fill_submissions_and_comments()
#db.close()
