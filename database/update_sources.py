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

def data_proc(source):
    content_list = []
    apos = u'\u0027'
    if source != "None":
        for item in source:
            d_item = {}
            for key in item.keys():
                data = item[key]
                #data = data.replace('"', '\\"')
                #data = data.replace("'", "\\'")
                data = data.strip()
                d_item[key] = data
            content_list.append(d_item)
        return content_list
    else :
        return "None"

if __name__ == '__main__':
    import sys
    file_name = './sources.json' 
    if len(sys.argv) == 2:
        file_name = sys.argv[1]
    news = json.load(codecs.open(file_name, 'r', 'utf-8'))
    conn, cursor, = sql_connect()

    for item in news:
        url = item['url']
        print(url)
        source = item['sources']
        sql = """
            UPDATE snopes_set
            SET sources_json = %s
            WHERE url = '%s'
            """%("%s", url)
        json_string = json.dumps(data_proc(source))
        rs = cursor.execute(sql, [json_string])
        

    conn.commit()
    sql_close(cursor, conn)

