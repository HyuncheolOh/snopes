import numpy as np
import json
import pandas as pd
import MySQLdb
import nltk
import math
import pandas as pd
import ast
import re
import operator
from draw_tools.bar_plot import BarPlot
from draw_tools.heatmap_plot import HeatmapPlot
from draw_tools.stacked_bar_plot import StackBarPlot
from draw_tools.pie_plot import PiePlot
from draw_tools.cdf_plot import CDFPlot

#sql connect
def sql_connect():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="fake_news", use_unicode=True, charset='utf8')
    cursor = conn.cursor()
    return conn, cursor

#sql close
def sql_close(cursor, conn):
    cursor.close()
    conn.close()

def news_count_veracity_with_source():
    sql = """
        SELECT veracity, count(*)
        FROM snopes_set
        WHERE sources != '[]' and veracity != 'None' 
        GROUP BY veracity
        ORDER BY count(*) desc
        LIMIT 6
        """

    cursor.execute(sql)
    rs = cursor.fetchall()

    news_count = {}
    for item in rs:
        source, count, = item
        news_count[source] = count
    return news_count

def news_count_veracity_without_source(veracity):
    sql = """
        SELECT veracity, count(*)
        FROM snopes_set
        WHERE sources = '[]' and veracity = '%s'
        GROUP BY veracity
        """%veracity

    cursor.execute(sql)
    rs = cursor.fetchall()

    veracity, count, = rs[0]

    return count

def sources():
    sql = """
        SELECT sources_json, category, url 
        FROM snopes_set
        """
        #WHERE sources != '[]'

    cursor.execute(sql)
    rs = cursor.fetchall()

    source_list = [item[0] for item in rs]
    category_list = [item[1] for item in rs]
    url_list = [item[2] for item in rs]

    return source_list, category_list, url_list

def sources_from_2017():
    sql = """
        SELECT sources_json, category, url 
        FROM snopes_set
        WHERE year(published_date) >= 2017
        """
        #WHERE sources != '[]'

    cursor.execute(sql)
    rs = cursor.fetchall()

    source_list = [item[0] for item in rs]
    category_list = [item[1] for item in rs]
    url_list = [item[2] for item in rs]

    return source_list, category_list, url_list


def sources_count():
    sql = """
        SELECT sources_json, veracity, post_id
        FROM snopes_set
        """
    
    cursor.execute(sql)
    rs = cursor.fetchall()

    source_list = [item[0] for item in rs]
    veracity_list = [item[1] for item in rs]
    postid_list = [item[2] for item in rs]

    return source_list, veracity_list, postid_list

def sources_count_from_2017():
    sql = """
        SELECT sources_json, veracity, post_id
        FROM snopes_set
        WHERE year(published_date) >= 2017
        """
    
    cursor.execute(sql)
    rs = cursor.fetchall()

    source_list = [item[0] for item in rs]
    veracity_list = [item[1] for item in rs]
    postid_list = [item[2] for item in rs]

    return source_list, veracity_list, postid_list


def veracity_types():
    sql = """
        SELECT veracity
        FROM snopes_set
        WHERE veracity != 'None' and year(published_date) >= 2017
        GROUP BY veracity
        ORDER BY count(*) desc
        LIMIT 6 
        """
    cursor.execute(sql)
    rs = cursor.fetchall()

    veracity_list = [item[0] for item in rs]

    return veracity_list

def source_num_by_article(tuples):
    source_list, category_list, url_list = tuples
    source_count_list = []
    for i, source in enumerate(source_list):
        source_count = 0
        if source == '"None"' or source== None:
            source_count = 0
        else:
            source_count = len(json.loads(source))
        source_count_list.append(source_count)

    return source_count_list

def article_num_by_source(source_dict, sources_json):
    #number of articles by source (press / book)
    for i, item in enumerate(sources_json):

        if item != "None" and item != None and item != '"None"':
            s_list = json.loads(item)
            
            #check whether this article already counted a press 
            source_in_article = []
            for sub_item in s_list:
                source_press = sub_item['press'].replace(".", "").strip()
                #print(source_press)
                
                if source_press == "":
                    continue

                if "The" not in source_press:
                    name_with_the = "The %s"%source_press 

                    if name_with_the in source_dict.keys():
                        source_press = name_with_the

                if source_press not in source_in_article:
                    source_dict[source_press] += 1
                    source_in_article.append(source_press)

    source_dict = {key: value for key, value in source_dict.items() if value is not 0}

    return source_dict 

def source_press_list(tuples):
    sources_json,_,_, = tuples
    source_dict = {}

    for s in sources_json:
        try :
            if s != "None" and s != None and s != '"None"':
                s_list = json.loads(s)
                for source_press in s_list:
                    press = source_press['press'].replace(".", "").strip()
                    if press != "":
                        source_dict[press] = 0

        except KeyError as e:
            continue

    return sources_json, source_dict


def source_num_by_veracity(tuples):
    sources_json, veracities, postids = tuples
    
    veracity_dict = {}
    for v in veracity_types():
        veracity_dict[v.lower()] = []

    max_num = 0
    max_postid = ''
    source_dict = {} 
    for i, item in enumerate(veracities):
        s = sources_json[i]
        #print(s)
        try :
            if s == "None" or s == None or s == '"None"':
                veracity_dict[item.lower().strip()].append(0)
            else :
                s_list = json.loads(s)
                for source_press in s_list:
                    press = source_press['press'].replace(".", "")
                    if press != "":
                        source_dict[press.strip()] = 0

                veracity_dict[item.lower().strip()].append(len(s_list))
        except KeyError as e:
            continue

    return veracity_dict

def top_source_by_category(category, veracity):
    condition = ''
    if veracity != 'all':
        condition = "and veracity = '%s'"%veracity

    sql = """
        SELECT sources_json
        FROM snopes_set
        WHERE category = '%s' %s
        """%(category, condition)
    
    cursor.execute(sql)
    rs = cursor.fetchall()

    source_list = [item[0] for item in rs]
    source_dict = {}
    for s in sources_json:
        try :
            if s != "None" and s != None and s != '"None"':
                s_list = json.loads(s)
                for source_press in s_list:
                    press = source_press['press'].replace(".", "").strip()
                    if press != "":
                        source_dict[press] = 0

        except KeyError as e:
            continue

    #source and article num count
    return article_num_by_source(source_dict, source_list)

    

if __name__ == "__main__":

    #numberof articles 
    total_count = 0

    #sql connect
    conn, cursor, = sql_connect()


    source_presence = ["exist", "not exist"]
    news_with_source = news_count_veracity_with_source()

    veracity_list = []
    news_count_exist = []
    news_count_not_exist = []
    source_all = []
    for item in news_with_source.keys():
        veracity_list.append(item)
        count1 = news_with_source[item]
        count2 = news_count_veracity_without_source(item)
        news_count_exist.append(count1)
        news_count_not_exist.append(count2)
#        print(item, count1, count2)
    source_all.append(news_count_exist)
    source_all.append(news_count_not_exist)

    StackBarPlt = StackBarPlot(np.arange(len(veracity_list)), source_all)
    StackBarPlt.set_xticks(veracity_list)
    StackBarPlt.set_legends(source_presence, "Source Presence")
    StackBarPlt.save_image('./image/veracity_by_source.png')

    #source exists articles
    '''
    #old source style. counting the number of years in the content
    regex = '[1-2][0-9][0-9][0-9].'
    source_count_list = []
    source_list, category_list, url_list = sources()
    for i, source in enumerate(source_list):
        u1ni = u'%s'%source
        uni = ast.literal_eval(uni)
        source_count = 0
        for item in uni:
            if bool(re.search(regex, item)) == True:
                source_count += 1
        
        source_count_list.append(source_count)
    count_list = [source_count_list.count(i) for i in range(30)]
    '''
    '''
    source_list, category_list, url_list = sources()
    source_count_list = []
    for i, source in enumerate(source_list):
        source_count = 0
        if source == '"None"' or source== None:
            source_count = 0
        else:
            source_count = len(json.loads(source))
        source_count_list.append(source_count)
    '''
    source_count_list = source_num_by_article(sources())
    source_count_list_from_2017 = source_num_by_article(sources_from_2017())

    max_num = max(source_count_list)
    max_num = 31
    print("max source num : %d"%max_num)
    count_list = [source_count_list.count(i) for i in range(max_num)]

    BarPlt = BarPlot(1)
    BarPlt.set_data(np.arange(max_num), count_list, "")
    BarPlt.set_width(0.8)
    BarPlt.set_xticks(np.arange(max_num))
    BarPlt.save_image("./image/source_num_bar.png")

    count_list = [source_count_list_from_2017.count(i) for i in range(max_num)]

    BarPlt = BarPlot(1)
    BarPlt.set_data(np.arange(max_num), count_list, "")
    BarPlt.set_width(0.8)
    BarPlt.set_xticks(np.arange(max_num))
    BarPlt.save_image("./image/source_num_bar_2017.png")


    #number of source distribution - cdf 
    Cdf = CDFPlot()
    Cdf.set_label('number of sources', 'CDF')
    Cdf.set_log(True)
    Cdf.set_data(source_count_list, "")
    Cdf.set_data(source_count_list_from_2017, "")
    Cdf.set_legends(["All", "year >=2017"])
    Cdf.save_image('./image/source_num_distribution_cdf.png')
    
    #number of articles distirbution by source - cdf
    
    veracity_list = veracity_types()
    sources_json, veracities, postids = sources_count()
    
    veracity_dict = {}
    for v in veracity_list:
        veracity_dict[v.lower()] = []

    max_num = 0
    max_postid = ''
    source_dict = {} 
    for i, item in enumerate(veracities):
        s = sources_json[i]
        #print(s)
        try :
            if s == "None" or s == None or s == '"None"':
                veracity_dict[item.lower().strip()].append(0)
            else :
                s_list = json.loads(s)
                for source_press in s_list:
                    press = source_press['press'].replace(".", "")
                    if press != "":
                        source_dict[press.strip()] = 0

                veracity_dict[item.lower().strip()].append(len(s_list))
        except KeyError as e:
            continue
    
    
    veracity_dict = source_num_by_veracity(sources_count())

    Cdf = CDFPlot()
    Cdf.set_label('number of sources', 'CDF')
    Cdf.set_log(True)
    legend_list = []
    for key in veracity_dict.keys():
        legend_list.append(key)
        Cdf.set_plot_data(veracity_dict[key], key)
    Cdf.set_legends(legend_list)
    Cdf.save_image('./image/source_distribution_veracity_cdf.png')

    veracity_dict = source_num_by_veracity(sources_count_from_2017())

    Cdf = CDFPlot()
    Cdf.set_label('number of sources', 'CDF')
    Cdf.set_log(True)
    legend_list = []
    for key in veracity_dict.keys():
        legend_list.append(key)
        Cdf.set_plot_data(veracity_dict[key], key)
    Cdf.set_legends(legend_list)
    Cdf.save_image('./image/source_distribution_veracity_2017_cdf.png')

    
    #print("number of press : %d"%len(source_dict.keys()))
    #sorted_dict = sorted(source_dict.items(), key=operator.itemgetter(1))
    #print(sorted_dict)
    #articles_num = [item[1] for item in source_dict]
    
    sources_json, source_dict = source_press_list(sources_count())
    sources_json_from_2017, source_dict_2017 = source_press_list(sources_count_from_2017())
    articles_num = article_num_by_source(source_dict, sources_json)
    articles_num_from_2017 = article_num_by_source(source_dict_2017, sources_json_from_2017)

    #remove number 0 keys because they were replaced with "The" name 
    Cdf = CDFPlot()
    Cdf.set_label('number of articles', 'CDF')
    Cdf.set_log(True)
    Cdf.set_data(articles_num.values(), '')
    Cdf.set_data(articles_num_from_2017.values(), '')
    Cdf.set_legends(["all", "year >= 2017"])
    Cdf.save_image('./image/articles_num_by_source_press_cdf.png')

    '''
    print("all-")
    for num in set(articles_num.values()):
        print("%d : %d"%(num, articles_num.values().count(num)))

    print("from 2017")
    for num in set(articles_num_from_2017.values()):
       print("%d : %d"%(num, articles_num_from_2017.values().count(num)))
    '''
    #top source media/press by category
    category_list = ["politics", "viral phenomena", "food", "science", "history", "medical", "fauxtography", "fake news", "politicians", "inboxer rebellion", "business", "crime", "entertainment"]

    
    for item in category_list:
        #sort by descending order
        result = top_source_by_category(item, 'mixture')
        result = sorted(result.items(), key = operator.itemgetter(1))
        result.reverse()

    
        print(item)
        for i in range(10):
            try :
                print("%s, %s"%(result[i][0], result[i][1]))
            except IndexError:
                continue












