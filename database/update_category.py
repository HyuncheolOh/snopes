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

def data_proc(data):
    data = data.replace('"', '\\"')
    data = data.replace("'", "\\'")
    return data

if __name__ == '__main__':
    import sys
    file_name = './category.json' 
    if len(sys.argv) == 2:
        file_name = sys.argv[1]
    news = json.load(codecs.open(file_name, 'r', 'utf-8'))
    conn, cursor, = sql_connect()

    for item in news:
        post_id = item['post_id']
        category = item['category']

        categories = category.split('_')
        if len(categories) > 1:
            main_category = categories[0].strip()
            sub_category = categories[1].strip()
            print(main_category, sub_category)        
            sql = """
                UPDATE snopes_set
                SET category='%s', sub_category='%s'
                WHERE post_id ='%s'
                """%(data_proc(main_category), data_proc(sub_category), post_id)
            rs = cursor.execute(sql)
            #if news already exists, then fetch next news
            cursor.execute(sql)


    conn.commit()
    sql_close(cursor, conn)

