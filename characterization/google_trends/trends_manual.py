from __future__ import division
import sys
sys.path.insert(0, '/media1/Fakenews/Snopes/characterization/draw_tools')

import MySQLdb
import nltk
import numpy as np
from cdf_plot import CDFPlot
from line_plot import LinePlot
from scatter_plot import ScatterPlot

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
        SELECT values_month, values_year, b.post_id, b.share_count, b.category, a.peak_at_publish
        FROM trends_manual a, snopes_set b 
        WHERE a.post_id = b.post_id  
        """

    cursor.execute(sql)
    rs = cursor.fetchall()

    values_month = [item[0] for item in rs]
    values_year = [item[1] for item in rs]
    post_ids = [item[2] for item in rs]
    sharecount_list = [item[3] for item in rs]
    categories = [item[4] for item in rs]
    peak = [item[5] for item in rs]
    #print(category_list)
    return values_month, values_year, post_ids, sharecount_list, categories, peak


def trim_trends(trend_values):
    result = []
    for item in trend_values:
        if item != '':
            a = map(int, item.split(','))
            result.append(np.array(a))

    max_len = len(max(result, key=len))
    r_result = []
    for item in result:
        if len(item) == max_len:
            r_result.append(item)

    print(max_len, len(r_result)) 
    return r_result
    #trend_values =  [map(int, item.split(',')) for item in trend_values if item != '']
   
    return trend_values
def get_legends(category_list):
    legends = []
    for item in category_list:
        if item != 'Viral Phenomena' and item != 'Politics' and item != 'Medical' and item != 'Fauxtography' and item != 'Fake News':
            legends.append('Others')
        else:
            legends.append(item)
    return legends

def get_marker(category_list):
    markers = []
    for item in category_list:
        if item == 'Viral Phenomena':
            markers.append('+')
        elif item == 'Politics':
            markers.append('^')
        elif item == 'Medical':
            markers.append('d')
        elif item == 'Fauxtography':
            markers.append('s')
        elif item == 'Fake News':
            markers.append('*')
        else : 
            markers.append('o')
    return markers

def get_peak_trends(post_ids, trend_values, sharecount_list, category_list, peak_list):
    trend = []
    ids = []
    shares = []
    category = []
    peaks = []
    for i, item in enumerate(trend_values):
        if item != '':
            a = map(int, item.split(','))
            if sharecount_list[i] > 300000:
                continue
            trend.append(np.array(a))
            ids.append(post_ids[i])
            shares.append(sharecount_list[i])
            category.append(category_list[i])
            peaks.append(peak_list[i])
    colors = []
    total_peak_trends = 0
    for i, item in enumerate(trend):
#        if item[15] == 100:
        if len(item) == 31 and 100 in item[13:18]:
            #print(ids[i], shares[i], category[i])
            total_peak_trends += 1
            colors.append('r')
        else : 
            colors.append('g')
            '''
            sql = """
                UPDATE trends_manual
                SET peak_at_publish = %s
                WHERE post_id = %s
                """
            cursor.execute(sql, [1, ids[i]])
            '''
#    conn.commit()
    
    print("num of peak trends : %d"%total_peak_trends)
    mean_trend = []
    for item in trend:
        mean_trend.append(np.mean(item[0:15]))
    markers = get_marker(category)
    legends = get_legends(category)
    Scatter = ScatterPlot()
    Scatter.set_log(True)
    Scatter.set_data(mean_trend, shares, colors, markers, legends)
    Scatter.set_ylim(100000)
    Scatter.save_image('../image/trends_sharecount_scatter.png')


if __name__ == '__main__':
    conn, cursor, = sql_connect()
    #trend_values, values_year = [trim_trends(value_month), trim_trends(value_year) for value_month, value_year in get_all_trends()]
    trend_month, trend_year, post_ids, sharecount_list, categories, peaks = get_all_trends()
    trend_mean = np.mean(np.array(trim_trends(trend_month)), axis=0).tolist()
    trend_year = np.mean(np.array(trim_trends(trend_year)), axis=0).tolist()

    LinePlt = LinePlot()
    LinePlt.set_label('days', 'trends')
    LinePlt.set_plot_data(trend_mean, 'Google Trends')
    LinePlt.set_ylim(100)
    LinePlt.save_image('../image/trends_mean_manual_line.png')

    LinePlt = LinePlot()
    LinePlt.set_label('weeks', 'trends')
    LinePlt.set_plot_data(trend_year, 'Google Trends')
    LinePlt.set_ylim(100)
    LinePlt.save_image('../image/trends_mean_manual_year_line.png')

    #get peak trend
    get_peak_trends(post_ids, trend_month, sharecount_list, categories, peaks)
    sql_close(cursor, conn)




