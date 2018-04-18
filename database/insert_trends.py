import MySQLdb 
import json
import codecs
import numpy as np

def sql_connect():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="fake_news", use_unicode=True, charset='utf8')
    cursor = conn.cursor()
    return conn, cursor

def sql_close(cursor, conn):
    cursor.close()
    conn.close()

def get_trends_data():
    sql = """
        SELECT post_id, published_date, dates, trend_values
        FROM trends
        WHERE trend_values != '' and published_date < '2018-03-15'
    """

    cursor.execute(sql)
    rs = cursor.fetchall()

    item_list = []
    for item in rs:
        post_id, published_date, dates, trend_values, = item

        item_list.append({'post_id' : post_id, 
            'published_date' : published_date, 
            'dates' : dates, 
            'trend_values' : trend_values})
    return item_list

def update_data(data):
    sql = """
        UPDATE trends
        SET increase_before = %s, increase_after = %s, rapid_increase = %s, variance = %s, stdev = %s, mean = %s, publish_date_value = %s
        WHERE post_id = %s
        """
        
    cursor.execute(sql, [data['increase_before'], data['increase_after'], data['rapid_increase'], data['variance'], data['stdev'], data['mean'], data['publish_date_value'], data['post_id']])
    conn.commit()

def analyze_trends(trend_values):

    #check three days of moving average 
    #10 11 / 12 13
    #14
    #15 16 / 17 18 
    trend_values = trend_values.replace('[','').replace(']','')
    trend_values = trend_values.replace('\n', '').split()
    trend_values = map(int, np.array(trend_values))
    print(trend_values)
    prev = 0
    moving_average = []
    for i in range(14):
        temp = trend_values[prev:(prev+3)]
        #print(temp, round(np.mean(temp),2))
        #print(temp)        
        moving_average.append(round(np.mean(temp),2))
        prev += 2 

    #print(moving_average)
    #check increase before
    #print(moving_average[2], moving_average[3], moving_average[4])

    #check moving average 3,4,5 increase
    increase_before = None
    if moving_average[4] < moving_average[5] and moving_average[5] < moving_average[6]:
#    if moving_average[3] < moving_average[4]:
        increase_before = True
    else :
        increase_before = False


    increase_after = None
    #check increase after
    if np.mean(trend_values[0:14]) < np.mean(trend_values[15:28]):
        increase_after = True
    else :
        increase_after = False

    rapid_increase = None
    #check rapid increase
    if np.mean(trend_values[11:14]) + 20 < np.mean(trend_values[14:17]):
        rapid_increase = True
    else :
        rapid_increase = False

    #print(np.mean(trend_values[11:14]), np.mean(trend_values[15:18]))

    #published day's trend value
    published_value = trend_values[14]
    #print(published_value)

    #mean
    print("mean ", np.mean(trend_values), np.mean(trend_values[0:14]), np.mean(trend_values[15:28]))
    print("variance ", np.var(trend_values))
    print("stdev ", np.std(trend_values))
    print("rapid_increase : %s"%rapid_increase)
    print("increase_after : %s"%increase_after)
    print("increase_before : %s"%increase_before)

    return {'mean':np.mean(trend_values), 'variance' : np.var(trend_values), 'stdev' : np.std(trend_values), 'rapid_increase' : rapid_increase, 'increase_after' : increase_after, 'increase_before' : increase_before, 'publish_date_value':trend_values[14]}

if __name__ == '__main__':
    conn, cursor, = sql_connect()

    trends_data = get_trends_data()

    for i, item in enumerate(trends_data):
        post_id = item['post_id']
        print(post_id)
        published_date = item['published_date']
        dates = item['dates']
        trend_values = item['trend_values']
        data = analyze_trends(trend_values)
        data['post_id'] = post_id
        update_data(data)


