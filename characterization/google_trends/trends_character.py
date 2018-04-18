from __future__ import division

import MySQLdb
import nltk
import numpy as np
from draw_tools.cdf_plot import CDFPlot
from draw_tools.line_plot import LinePlot

#sql connect
def sql_connect():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="fake_news", use_unicode=True, charset='utf8')
    cursor = conn.cursor()
    return conn, cursor

#sql close
def sql_close(cursor, conn):
    cursor.close()
    conn.close()

def get_all_trends():
    sql = """
        SELECT trend_values
        FROM trends a, snopes_set b 
        WHERE a.post_id = b.post_id and trend_values != '' and a.published_date < '2018-03-15' 
        """

    cursor.execute(sql)
    rs = cursor.fetchall()

    trend_values = [item[0] for item in rs]
    
    #print(category_list)
    return trend_values

def get_categories():
    sql = """
        SELECT b.category
        FROM trends a, snopes_set b 
        WHERE a.post_id = b.post_id and trend_values != '' and a.published_date < '2018-03-15' 
        GROUP BY b.category
        HAVING count(*) > 10
        """

    cursor.execute(sql)
    rs = cursor.fetchall()

    category_list = [item[0] for item in rs]
    
    #print(category_list)
    return category_list

def get_trends_data(veracity):
    sql = """
        SELECT increase_before, increase_after, rapid_increase
        FROM trends a, snopes_set b 
        WHERE a.post_id = b.post_id and trend_values != '' and a.published_date < '2018-03-15' and b.veracity = '%s'
        """%(veracity)

    cursor.execute(sql)
    rs = cursor.fetchall()

    before_list = [item[0] for item in rs]
    after_list = [item[1] for item in rs]
    rapid_list = [item[2] for item in rs]

    return before_list, after_list, rapid_list

def get_trends_data_with_category(category):
    sql = """
        SELECT increase_before, increase_after, rapid_increase
        FROM trends a, snopes_set b 
        WHERE a.post_id = b.post_id and trend_values != '' and a.published_date < '2018-03-15' and b.category = '%s'
        """%(category)

    cursor.execute(sql)
    rs = cursor.fetchall()

    before_list = [item[0] for item in rs]
    after_list = [item[1] for item in rs]
    rapid_list = [item[2] for item in rs]

    return before_list, after_list, rapid_list


def trim_trends(trend_values):
    trend_values = trend_values.replace('[','').replace(']','')
    trend_values = trend_values.replace('\n', '').split()
    trend_values = map(int, np.array(trend_values))

    return trend_values
        
if __name__ == '__main__':
    conn, cursor, = sql_connect()
    trend_values = [trim_trends(value) for value in get_all_trends()]
    LinePlt = LinePlot()
    LinePlt.set_label('days', 'trends')
    LinePlt.set_plot_data(trend_values, 'Google Trends')
    #LinePlt.set_xticks(range(2011, 2018))
    #LinePlt.set_legends(category_all)
    LinePlt.save_image('./image/trends_line.png')

    #draw with mean value 
    trend_values = np.array(trend_values)
    trend_mean =np.mean(trend_values, axis=0)
    print(trend_mean)
    trend_mean = trend_mean.tolist()
    print(trend_mean)
    LinePlt = LinePlot()
    LinePlt.set_label('days', 'trends')
    LinePlt.set_plot_data(trend_mean, 'Google Trends')
    #LinePlt.set_xticks(range(2011, 2018))
    #LinePlt.set_legends(category_all)
    LinePlt.set_ylim(100)
    LinePlt.save_image('./image/trends_mean_line.png')

    sql_close(cursor, conn)




