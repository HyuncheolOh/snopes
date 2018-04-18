from __future__ import print_function

import numpy as np
import pandas as pd
import MySQLdb
import nltk
import math
from draw_tools.box_plot import BoxPlot
from draw_tools.cdf_plot import CDFPlot
from draw_tools.bar_plot import BarPlot
from draw_tools.stacked_bar_plot import StackBarPlot
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

def article_number_by_category():
    sql = """
        SELECT category, count(*)
        FROM snopes_set
        WHERE category != 'uncategorized'
        GROUP BY category
        ORDER BY count(*) desc
        """

    cursor.execute(sql)
    rs = cursor.fetchall()

    category_list = [item[0] for item in rs]
    count_list = [item[1] for item in rs]

    return category_list, count_list

def category_list_with_verdict():
    sql = """
        SELECT category
        FROM snopes_set
        WHERE category != 'uncategorized' and (veracity='False' or veracity='True' or veracity = 'Mixture')
        GROUP BY category
        ORDER BY count(*) desc
        """

    cursor.execute(sql)
    rs = cursor.fetchall()

    category_list = [item[0] for item in rs]

    return category_list

def article_num_by_year(year, month):
    sql = """
        SELECT count(*)
        FROM snopes_set
        WHERE year(published_date) = %s and month(published_date) = %s
        """

    cursor.execute(sql, [year, month])
    rs = cursor.fetchall()

    count = rs[0][0]
    return count


def article_num_by_year_verdict(year, month, verdict):
    sql = """
        SELECT count(*)
        FROM snopes_set
        WHERE year(published_date) = %s and month(published_date) = %s and veracity = %s
        """

    cursor.execute(sql, [year, month, verdict])
    rs = cursor.fetchall()

    count = rs[0][0]
    return count



def article_number_by_category_verdict(category, verdict):
    sql = """
        SELECT count(*)
        FROM snopes_set
        WHERE category != 'uncategorized' and category = %s and veracity=%s
        """
    cursor.execute(sql, [category, verdict])
    rs = cursor.fetchall()

    count_list = rs[0][0] 

    return count_list

if __name__ == "__main__":

    conn, cursor = sql_connect()

    verdict = ["True", "False", "Mixture"]
    #number of articles by category 
    #bar plot
    print("number of articles by category")
    category_list, count_list = article_number_by_category()
    Bar = BarPlot(1)
    Bar.set_data(category_list, count_list, '', 'vertical')
    Bar.set_width(0.6)
    Bar.save_image('./image/num_articles_by_category_bar.png')
    
    print("number of articles by category with veracity")
    #numberof articles by category with verdict - stacked_bar
    category_list = category_list_with_verdict()
    count_all = []
    for v in verdict:
        verdict_count = []
        for category in category_list:
            num = article_number_by_category_verdict(category, v)
            verdict_count.append(num)
        #    print(num, end = ',')
        #print()
        count_all.append(verdict_count)
    StackBar = StackBarPlot(np.arange(len(category_list)), count_all)
    StackBar.set_xticks(category_list, 'vertical')
    StackBar.set_legends(verdict, "Verdict")
    StackBar.set_width(0.6)
    StackBar.save_image('./image/num_article_by_category_verdict_stackbar.png')

    #num of articles by year and month
    print("number of articles by year and month");
    year_list = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]
    month_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    subplot_num = lambda x : int(math.sqrt(x)) if math.sqrt(x).is_integer() else int(math.sqrt(x)) + 1
    Bar = BarPlot(subplot_num(len(year_list)))
    for year in year_list:
        num_list = []
        for month in month_list:
            num = article_num_by_year(year, month)
            if year == 2018 and month >=4:
                num = 0
            num_list.append(num)

        Bar.set_data(np.arange(len(month_list)) + 1, num_list, year)
        Bar.set_width(0.6)
        Bar.set_ylim(250)

    Bar.save_image('./image/num_articles_by_year_month_bar.png')
    
    print("number of articles by year and month with veracity");
    #num of articles by year and month with true / false / mixture
    StackBar = StackBarPlot(0, 0, subplot_num(len(year_list))) 
    for year in year_list:
        num_list = []
        for v in verdict:
            verdict_count = [] 
            for month in month_list:
                num = article_num_by_year_verdict(year, month, v)
                if year == 2018 and month >=4:
                    num = 0
                verdict_count.append(num)
            num_list.append(verdict_count)
        StackBar.set_data(np.arange(len(month_list)), num_list, year)
        StackBar.set_xticks(np.arange(len(month_list)) + 1)
        StackBar.set_width(0.6)
        StackBar.set_ylim(200)
        #StackBar.set_legends(verdict, "Verdict")
    StackBar.save_image('./image/num_articles_by_year_month_verdict_stackbar.png')

        
            


    sql_close(cursor, conn)



