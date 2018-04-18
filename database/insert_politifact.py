import MySQLdb 
import json
import codecs
import numpy as np
import re
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

    #json_data = json.load(open('./data/true.json')) 
    json_data = json.load(open('./data/false.json')) 

    p = re.compile("(\d+)+(\D+)")
    for item in json_data:

        title = item['text']
        veracity = item['verdict']
        date = item['date']
        number = p.search(date).group(1)
        date = p.sub(number + ' ', date)
        date = parser.parse(date)
        source = 'Politifact'
        print(title, date)
        sql = """
            INSERT other_data (title, dates, veracity, source)
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(sql, [title, date, veracity, source])
    conn.commit()
    sql_close(cursor,conn)



