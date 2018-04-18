import numpy as np
import json
import pandas as pd
import MySQLdb
import csv
import codecs
from dateutil import parser
from pytrends.request import TrendReq
from datetime import datetime, timedelta
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from time import sleep

#sql connect
def sql_connect():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="fake_news", use_unicode=True, charset='utf8')
    cursor = conn.cursor()
    return conn, cursor

#sql close
def sql_close(cursor, conn):
    cursor.close()
    conn.close()

def get_high_sharecount_artcile():
    sql = """
        SELECT post_id, title, share_count, published_date
        FROM snopes_set
        WHERE year(published_date) >= 2004
        ORDER BY share_count desc
        """
    
    cursor.execute(sql)
    rs = cursor.fetchall()

    article_list = []

    for item in rs:
        post_id, title, share_count, published_date, = item
        article_list.append({'post_id': post_id, 'title' : title, 'share_count' : share_count, 'published_date' : published_date})
    
    return article_list

def insert_date_in_db(post_id, title, key_word, published_date, dates_month, values_month, dates_year, values_year):
    sql = """
        INSERT IGNORE INTO trends_manual(
            post_id, title, key_word, published_date, dates_month, values_month, dates_year, values_year
        )
        VALUES (
             %s, %s, %s, %s, %s, %s, %s, %s
        )"""

    cursor.execute(sql, [post_id, title, key_word, published_date, dates_month, values_month, dates_year, values_year])
    conn.commit()

def is_in_trends_db(post_id):
    sql = """
        SELECT post_id
        FROM trends_manual
        WHERE post_id = '%s'
        """%post_id

    cursor.execute(sql)
    rs = cursor.fetchall()
    if len(rs) !=0:
        return True
    else :
        return False

#return +/- 3 months
def get_timeframe_month(published_date):
    start_time = published_date - timedelta(days=15)
    end_time = published_date + timedelta(days=15)
    return '%s %s'%(start_time.strftime('%Y-%m-%d'), end_time.strftime('%Y-%m-%d'))

def get_timeframe_year(published_date):
    start_time = published_date - timedelta(days=180)
    end_time = published_date + timedelta(days=180)
    return '%s %s'%(start_time.strftime('%Y-%m-%d'), end_time.strftime('%Y-%m-%d'))

def get_checkdate(num, published_date):
    start_time = published_date - timedelta(days=num)
    return start_time.strftime('%Y-%m-%d')


def get_trends(kw_list, periods):
    #print(kw_list, periods)
    pytrends = TrendReq()
    #cat 0 is all categories
    pytrends.build_payload(kw_list, cat=0, timeframe=periods)
    return pytrends.interest_over_time()

def get_keywords(df, key_word, published_date):
    weight = 0
    #print(key_word, published_date)
    #1.if publisehd date has 100 trends 
    date_range = pd.date_range(published_date.strftime('%Y-%m-%d'), periods=1)
    
    published_date_df = df[df.index.isin(date_range)]
    #print(published_date_df[key_word])
    if published_date_df[key_word][0] == 100:
        #print("trend 100 at published date")
        weight += 10000

    #2. if there is 100 trends within 1 week (6 days)
    date_range = pd.date_range(get_checkdate(3, published_date), periods = 6)
    published_date_df = df[df.index.isin(date_range)]
    if 100 in published_date_df[key_word]:
        #print("trend 100 within 1 week from published date")
        weight += 1000

    #2.if there is 100 trends within check date
    date_range = pd.date_range(get_checkdate(14, published_date), periods = 28)
    published_date_df = df[df.index.isin(date_range)]
    if 100 in published_date_df[key_word]:
        #print("trend 100 within 1 month from published date")
        weight += 100
        
    #3.if mean average is high within check date
    if weight == 0:
        mean = published_date_df[key_word].mean()
        #print("mean : %s"%mean)
        weight = mean

    return weight, published_date_df

if __name__ == '__main__':
    conn, cursor, = sql_connect()

    #load csv file 
    f = open('./trend_keyword.csv', 'r')
    article_list = csv.reader(f)
    for i, item in enumerate(article_list):
        
        if i == 0 :
            continue
        post_id = item[0]
        claim = item[5]
        published_date = item[4]
        published_date = parser.parse(published_date)
        words = item[6]
        postid_exist = is_in_trends_db(post_id)
        if postid_exist:
            continue
        print(item)
        #month timeframe
        time_frame = get_timeframe_month(published_date)
        print(time_frame)
        
        candidate_df = get_trends([words], time_frame)
        dates_month = candidate_df.index.values
        values_month = []
        if len(dates_month) != 0:
            values_month = candidate_df[words].values
            dates_month = ','.join(map(str, dates_month))
            values_month = ','.join(map(str, values_month))
        else :
            values_month = ''
            dates_month = ''
        
        time_frame = get_timeframe_year(published_date)
        print(time_frame)
        
        candidate_df = get_trends([words], time_frame)
        dates_year = candidate_df.index.values
        if len(dates_year) != 0:
            values_year = candidate_df[words].values
            dates_year = ','.join(map(str, dates_year))
            values_year = ','.join(map(str, values_year))
        else :
            values_year = ''
            dates_year = ''


        insert_date_in_db(post_id,claim, words, published_date, dates_month, values_month, dates_year, values_year)
        #print(post_id, claim, words, dates_month, values_month, dates_year, values_year)
    

#    key_word = 'donald trump'
#    df = get_trends(key_word)
#    print(type(df))
#    df.to_csv('./google_trends/%s.csv'%key_word)
    sql_close(cursor, conn)
