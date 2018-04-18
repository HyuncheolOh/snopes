import MySQLdb 
import json
import codecs

def sql_connect():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="fake_news", use_unicode=True, charset='utf8')
    cursor = conn.cursor()
    return conn, cursor

def sql_close(cursor, conn):
    cursor.close()
    conn.close()

def data_trim(data):
    data = data.replace('"', '\\"')
    data = data.replace("'", "\\'")
    return data

if __name__ == '__main__':
    import sys
    file_name = './update.json' 
    if len(sys.argv) == 2:
        file_name = sys.argv[1]
    news = json.load(codecs.open(file_name, 'r', 'utf-8'))
    conn, cursor, = sql_connect()

    for item in news:
        #load existing news
        url = item['url']
        veracity = item['veracity']
        
        if veracity == None:
            continue

        if "Real" in veracity:
            veracity = u'True'

        if "Multiple" in veracity:
            veracity = u'Mixture'

        if "Hoax" in veracity:
            veracity = u'False'

        if len(veracity) > 16:
            veracity = None

        print(url, veracity)
        sql = """
            UPDATE snopes_set
            SET veracity='%s' 
            WHERE url ='%s'
            """%(veracity, url)
        rs = cursor.execute(sql)
        #print(url) 
        #if news already exists, then fetch next news
        cursor.execute(sql)
        
    conn.commit()
    sql_close(cursor, conn)



