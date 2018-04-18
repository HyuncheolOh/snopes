import numpy as np
import json
import pandas as pd
import MySQLdb
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

def insert_date_in_db(post_id, title, key_word, published_date, indices, values):
    sql = """
        INSERT IGNORE INTO trends(
            post_id, title, key_word, published_date, dates, trend_values
        )
        VALUES (
             %s, %s, %s, %s, %s, %s
        )"""

    cursor.execute(sql, [post_id, title, key_word, published_date, indices, values])
    conn.commit()

def is_in_trends_db(post_id):
    sql = """
        SELECT post_id
        FROM trends
        WHERE post_id = '%s'
        """%post_id

    cursor.execute(sql)
    rs = cursor.fetchall()
    if len(rs) !=0:
        return True
    else :
        return False

#return +/- 3 months
def get_timeframe(published_date):
    start_time = published_date - timedelta(days=90)
    end_time = published_date + timedelta(days=90)

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

def n_grams(n, sentence):
    #split
    tokenizer = RegexpTokenizer(r'\w+')
    word_tokens = tokenizer.tokenize(sentence.lower())
    
    stop_words = set(stopwords.words('english'))
    word_tokens = [w for w in word_tokens if not w in stop_words]

    #select words n times 
    words_list = []
    if n == 2:

        for i in range(0,len(word_tokens)):
            for j in range(i+1,len(word_tokens)):
                word1 = word_tokens[i]
                word2 = word_tokens[j]
                print(word1, word2)
    elif n==3:
        for i in range(0, len(word_tokens)):
            for j in range(i+1, len(word_tokens)):
                for k in range(j+1, len(word_tokens)):
                    word1 = word_tokens[i]
                    word2 = word_tokens[j]
                    word3 = word_tokens[k]
                    words_list.append('%s %s %s'%(word1, word2, word3))
#                    print(word1, word2, word3)

    return words_list

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

    article_list = get_high_sharecount_artcile()
    for item in article_list:
        title = item['title']
        post_id = item['post_id']
        words_list = n_grams(3, title)
        time_frame = get_timeframe(item['published_date'])
        published_date = item['published_date']
        max_weight = 0
        candidate_index = -1
        candidate_df = 0
        
        postid_exist = is_in_trends_db(post_id)
        if postid_exist:
            continue

        print(post_id, title)
        index_list = weight_list = []
        for i, words in enumerate(words_list):
            #sleep(60)
            print("get trends : %s, %s"%(words, time_frame))
            df = get_trends([words], time_frame)
            if len(df) != 0:

                weight, _candidate_df = get_keywords(df, words, published_date)
                index_list.append(i)
                weight_list.append(weight)

                if weight > max_weight:
                    max_weight = weight
                    candidate_index = i
                    candidate_df = _candidate_df

                if weight >= 1000:
                    break

            #sleep 60 seconds to prevent from blocking by google
            print(i, words)
        if candidate_index == -1:
            insert_date_in_db(post_id, title, '', '', '', '')
            continue
        
        indices = candidate_df.index.values
        values = candidate_df[:-1][words_list[candidate_index]].values
        key_word = words_list[candidate_index]
        insert_date_in_db(post_id, title, key_word, published_date, indices, values)
        print(post_id, title, key_word)

    

#    key_word = 'donald trump'
#    df = get_trends(key_word)
#    print(type(df))
#    df.to_csv('./google_trends/%s.csv'%key_word)
    sql_close(cursor, conn)
