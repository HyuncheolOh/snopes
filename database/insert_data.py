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

def data_trim(data):
    if data == None:
        return data
    data = data.replace('"', '\\"')
    data = data.replace("'", "\\'")
    data = data.replace('%', '%%')
    return data

   
def list_pre_proc(data):
    for i in range(len(data)):
        data[i] = data[i].replace('"', '\\"')
    return data

if __name__ == '__main__':
    import sys
    file_name = './data.json' 
    if len(sys.argv) == 2:
        file_name = sys.argv[1]
    news = json.load(codecs.open(file_name, 'r', 'utf-8'))
    conn, cursor, = sql_connect()

    c_n = 0
    u_n = 0
    t_n = 0
    s_n = 0
    v_n = 0
    d_n = 0

    for item in news:
        
        #load existing news
        sql = """
            SELECT * 
            FROM snopes_set
            WHERE post_id ='%s'
            """%(item['post_id'])
        rs = cursor.execute(sql)
    
        #if news already exists, then fetch next news
        if rs == 1:
            continue
       
#        if item['post_id'] != "30347":
#            continue
        print("post_id : %s"%item['post_id'])
#        print(item)
        veracity = item['veracity']
        claim = item['claim']
        share = item['share_count']
        source = item['sources']
        url = item['url']
        tag = item['tag']
        category = item['category']
        main_category = category
        sub_category = ''
        categories = category.split('_')
        if len(categories) > 1:
            main_category = categories[0].strip()
            if main_category == 'Fraud &amp; Scams':
                main_category = main_category.replace('&amp;', '&')
            sub_category = categories[1].strip()
        
        description = item['detailed_description']
        if claim == None:
            c_n +=1

        if share == None:
            s_n += 1

        if veracity == None:
            v_n += 1

        if description == None or len(description) == 0:
            d_n += 1

        if url == None:
            u_n +=1

        if tag == None or len(tag) == 0:
            t_n += 1

        if veracity == None:
            veracity = "None"

        if len(veracity) > 16:
            veracity = "OHTERS"

        share = share.replace('K', '000')
        share = share.replace('M', '000000')
        
        sql = """
            INSERT IGNORE INTO snopes_set (
                post_id, category, sub_category, title, veracity, url, published_date, modified_date, description, share_count, fact_checker, claim, sources_json, tag, detailed_description 
            ) 
            VALUES (
                "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", %s, "%s", %s
            )"""%(item['post_id'], data_trim(main_category), data_trim(sub_category), data_trim(item['title']), veracity, item['url'], item['published_date'], item['modified_date'], data_trim(item['description']), share, item['fact_checker'], data_trim(item['claim']), "%s", data_trim(",".join(item['tag'])),  "%s")
        cursor.execute(sql, [json.dumps(data_proc(item['sources'])), str(item['detailed_description'])])
        
    conn.commit()
        
    sql_close(cursor, conn)

    print("Number of articles : %s"%len(news))
    print("None Count")
    print("Claim : %d"%c_n)
    print("Share : %d"%s_n)
    print("Veracity : %d"%v_n)
    print("URL : %d"%u_n)
    print("TAG : %d"%t_n)
    print("Description : %d"%d_n)


