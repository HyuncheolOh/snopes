import numpy as np
import pandas as pd
import MySQLdb
import nltk
import math
from draw_tools.box_plot import BoxPlot
from draw_tools.cdf_plot import CDFPlot
from nltk.tokenize import word_tokenize

#sql connect
def sql_connect():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="fake_news", use_unicode=True, charset='utf8')
    cursor = conn.cursor()
    return conn, cursor

#sql close
def sql_close(cursor, conn):
    cursor.close()
    conn.close()

def get_verbs(data):
    tagged_data = nltk.pos_tag(data)
    verbs = [word for word, pos in tagged_data \
            if (pos.startswith('V'))]
    return verbs

def sql_quotation(data):
    data = data.replace("'", "\\'")
    data = data.replace('"', '\\"')
    return data


def sharecount_cdf(date_condition, file_name):
    sql = """
        SELECT post_id, share_count
        FROM snopes_set
        WHERE published_date %s  
        """%date_condition
    cursor.execute(sql)
    rs = cursor.fetchall()

    sharecount_list = []
    for item in rs:
        post_id, share_count, = item
        sharecount_list.append(int(share_count))

    #Display CDF and save at the path
    Cdf = CDFPlot()
    Cdf.set_label('share_count', 'CDF') 
    Cdf.set_log(True)
    Cdf.set_data(sharecount_list, "")
    Cdf.save_image('./image/sharecount_%s.png'%file_name)

    return sharecount_list

def sharecount_by_category(category):
    sql = """
        SELECT share_count
        FROM snopes_set
        WHERE category = '%s'  
        """%sql_quotation(category)

    cursor.execute(sql)
    rs = cursor.fetchall()

    sharecount_list = []
    for item in rs:
        share_count, = item
        sharecount_list.append(share_count)
    return sharecount_list

def sharecount_by_category_with_source(category):
    sql = """
        SELECT share_count
        FROM snopes_set
        WHERE category = '%s' and sources != '[]' and year(published_date) >= 2017
        """%sql_quotation(category)

    cursor.execute(sql)
    rs = cursor.fetchall()

    sharecount_list = []
    for item in rs:
        share_count, = item
        sharecount_list.append(share_count)
    return sharecount_list

def sharecount_by_category_without_source(category):
    sql = """
        SELECT share_count
        FROM snopes_set
        WHERE category = '%s' and sources = '[]' and year(published_date) >= 2017
        """%sql_quotation(category)

    cursor.execute(sql)
    rs = cursor.fetchall()

    sharecount_list = []
    for item in rs:
        share_count, = item
        sharecount_list.append(share_count)
    return sharecount_list


def category_list():
    sql = """
        SELECT category
        FROM snopes_set
        GROUP BY category
        ORDER BY count(*) desc
        """
    
    cursor.execute(sql)
    rs = cursor.fetchall()

    category_list = []
    for item in rs:
        category, = item
        category_list.append(category)
    return category_list

def sharecount_per_month(year, month):
     #news per month, year
    sql = """
        SELECT share_count
        FROM snopes_set
        WHERE year(published_date) = '%s' and month(published_date) = '%s' 
        """%(year, month)

    cursor.execute(sql)
    rs = cursor.fetchall()
        
    value = []
    for item in rs:
        share_count, = item
        value.append(share_count)
   
    return value

def sharecount_by_sources(source_bool):
    condition = ''

    if source_bool == True:
        condition = """sources_json is not NULL and sources_json != '"None"'"""
    else :
        condition = """sources_json is NULL or sources_json = '"None"'"""

    sql = """
        SELECT share_count
        FROM snopes_set
        WHERE %s
        """%condition

    cursor.execute(sql)
    rs = cursor.fetchall()

    return [item[0] for item in rs]

def sharecount_by_sources(source_bool):
    condition = ''

    if source_bool == True:
        condition = """sources_json is not NULL and sources_json != '"None"' and year(published_date) >= 2017"""
    else :
        condition = """sources_json is NULL or sources_json = '"None"' and year(published_date) >= 2017"""

    sql = """
        SELECT share_count
        FROM snopes_set
        WHERE %s
        """%condition

    cursor.execute(sql)
    rs = cursor.fetchall()

    return [item[0] for item in rs]
   

if __name__ == "__main__":

    #numberof articles 
    total_count = 0

    #sql connect
    conn, cursor, = sql_connect()
    total_list = sharecount_cdf("<= date(now())", "total")
    sub_total_list = sharecount_cdf("< '2018-03-01'", "2018_02")
    Cdf = CDFPlot()
    Cdf.set_label('share_count', 'CDF') 
    Cdf.set_log(True)
    Cdf.set_data(total_list, "total")
    Cdf.set_data(sub_total_list, "< 2018.02")
    Cdf.save_image('./image/sharecount_%s.png'%"comparison")

    sharecount_cdf("between '2016-01-01' and '2018-03-01'", "2016_2018")
        
    #share count per year 
    year = ["'2010-01-01' and '2010-12-31'", "'2011-01-01' and '2011-12-31'", "'2012-01-01' and '2012-12-31'", 
            "'2013-01-01' and '2013-12-31'", "'2014-01-01' and '2014-12-31'", "'2015-01-01' and '2015-12-31'", 
            "'2016-01-01' and '2016-12-31'", "'2017-01-01' and '2017-12-31'"]
    for date in year:
        sharecount_cdf("between " + date, date[1:5])
   
    category_list = category_list()
    all_sharecount_list = []
    for item in category_list:
        #sharecount list of one category
        all_sharecount_list.append(sharecount_by_category(item))
    
    subplot_num = lambda x : int(math.sqrt(x)) if math.sqrt(x).is_integer() else int(math.sqrt(x)) + 1
 
    #Display BoxPlot and save at the path
    BoxPlt = BoxPlot(subplot_num(25))
    for i in range(25):
        BoxPlt.set_data(all_sharecount_list[i],'')
        BoxPlt.set_title(category_list[i])
        BoxPlt.set_ylim(1000)

    BoxPlt.save_image('./image/sharecount_box_plot.png')

    all_sharecount_list = []
    #category with source presence
    for item in category_list:
        all_sharecount_list.append([sharecount_by_category_with_source(item), sharecount_by_category_without_source(item)])
 
    #Display BoxPlot and save at the path
    BoxPlt = BoxPlot(subplot_num(25))
    for i in range(25):
        BoxPlt.set_data(all_sharecount_list[i],'')
        BoxPlt.set_title(category_list[i])
#        BoxPlt.set_ylim(2000)

    BoxPlt.save_image('./image/sharecount_sources_boxplot.png')
    
 
    #share count per month
    year_list = ["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018"]
    month_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

    year_value = []
    for year in year_list:
        month_value = []
        for month in month_list:
            month_value.append(sharecount_per_month(year, month))
        year_value.append(month_value)
    
    BoxPlt = BoxPlot(1)
    for i in range(len(year_value)):
        grid = str(len(year_value)) + str(1) + str(i+1)
        BoxPlt.set_data_with_position(year_value[i], '', int(grid))
        BoxPlt.set_title(year_list[i])
    BoxPlt.save_image('./image/sharecount_month_boxplot.png')

    #share count by an article - cdf with 2017, all 

    source_exist_sharecount = sharecount_by_sources(True)
    source_no_sharecount = sharecount_by_sources(False)

    Cdf = CDFPlot()
    Cdf.set_label('share_count', '') 
    Cdf.set_log(True)
    Cdf.set_data(source_exist_sharecount, "")
    Cdf.set_data(source_no_sharecount, "")
    Cdf.set_legends(["Source exist", "Source not exist"])
    Cdf.save_image('./image/sharecount_num_by_source_cdf.png')

    #since 2017
    source_exist_sharecount = sharecount_by_sources(True)
    source_no_sharecount = sharecount_by_sources(False)

    Cdf = CDFPlot()
    Cdf.set_label('share_count', '') 
    Cdf.set_log(True)
    Cdf.set_data(source_exist_sharecount, "")
    Cdf.set_data(source_no_sharecount, "")
    Cdf.set_legends(["Source exist", "Source not exist"])
    Cdf.save_image('./image/sharecount_num_by_source_2017_cdf.png')


    sql_close(cursor, conn)


