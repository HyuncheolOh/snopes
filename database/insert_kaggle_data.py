import MySQLdb 
import json
import codecs
import numpy as np
import re
import csv
import sys
from datetime import datetime
from dateutil import parser



def sql_connect():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="fake_news", use_unicode=True, charset='utf8')
    conn.set_character_set('utf8mb4')
    cursor = conn.cursor()
    return conn, cursor

def sql_close(cursor, conn):
    cursor.close()
    conn.close()

if __name__ == '__main__':
    conn, cursor, = sql_connect()

    csv.field_size_limit(sys.maxsize)

    with open('fake.csv', 'r') as csvfile:
        content = csv.reader(csvfile)

        sql = """
            INSERT kaggle_data (uuid, ord_in_thread, author, published, title, description, language, crawled, site_url, country, domain_rank, thread_title, spam_score, main_img_url, replies_count, participants_count, likes, comments, shares, type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

        for i, item in enumerate(content):
            if i == 0 :
                continue
            if '' in item[10]:
                item[10] = 0
            cursor.execute(sql, [item[0], item[1], item[2], parser.parse(item[3]), item[4], '',item[6],parser.parse(item[7]),item[8],item[9],item[10],item[11],item[12],item[13],item[14],item[15],item[16],item[17],item[18],item[19]])
            #print(item[3])
            #print(item[3][:10])
            #print(parser.parser(item[3]))

    conn.commit()
    sql_close(cursor,conn)



