import MySQLdb 
import json
import codecs
import numpy as np
import re
import csv
from datetime import datetime
from dateutil import parser

def sql_connect():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="fake_news", use_unicode=True, charset='utf8')
    cursor = conn.cursor()
    return conn, cursor

def sql_close(cursor, conn):
    cursor.close()
    conn.close()

if __name__ == '__main__':
    conn, cursor, = sql_connect()

    with open('factcheckorg.csv', 'r') as csvfile:
        content = csv.reader(csvfile)

        for i, item in enumerate(content):
            if i == 0:
                continue
            title = item[0]
            date = item[1]
            veracity = item[2]
            source = item[3]
            print(item)
            sql = """
            INSERT other_data (title, dates, veracity, source)
            VALUES (%s, %s, %s, %s)
            """

            cursor.execute(sql, [title, date, veracity, source])


    conn.commit()
    sql_close(cursor,conn)



