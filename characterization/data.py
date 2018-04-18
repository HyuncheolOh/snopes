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
        ORDER BY share_count desc
        """
    
    cursor.execute(sql)
    rs = cursor.fetchall()

    article_list = []

    for item in rs:
        post_id, title, share_count, published_date, = item
        if published_date != None:
            try :
                published_date = published_date.strftime('%Y-%m-%d')
            except ValueError: 
                published_date = '0'    
        article_list.append({'post_id': post_id, 'title' : title, 'share_count' : share_count, 'published_date' : published_date})
    
    return article_list

if __name__ == '__main__':
    conn, cursor, = sql_connect()

    article_list = get_high_sharecount_artcile()
    with open('./snopes_data.json', 'w') as outfile:
        json.dump(article_list, outfile)
    
    sql_close(cursor, conn)
