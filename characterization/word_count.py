import MySQLdb 
import json
import re
import operator
import pandas as pd
import nltk
from draw_tools.line_plot import LinePlot
from textblob import TextBlob

def sql_connect():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="fake_news", use_unicode=True, charset='utf8')
    cursor = conn.cursor()
    return conn, cursor

def sql_close(cursor, conn):
    cursor.close()
    conn.close()

def titles(year, month):
#    print("%s.%s"%(year, month))
    sql = """
        SELECT title
        FROM snopes_set
        WHERE year(published_date) = '%s' and month(published_date) = '%s'
        """%(year, month)

    cursor.execute(sql)
    rs = cursor.fetchall()

    return [item[0] for item in rs]
def titles_year(year):
    #print("%s"%(year))
    sql = """
        SELECT title
        FROM snopes_set
        WHERE year(published_date) = '%s' 
        """%(year)

    cursor.execute(sql)
    rs = cursor.fetchall()

    return [item[0] for item in rs]

def titles_year_category(year, category):
    #print("%s , %s"%(year, category))
    sql = """
        SELECT title
        FROM snopes_set
        WHERE year(published_date) = '%s' and category = '%s'
        """%(year, category)

    cursor.execute(sql)
    rs = cursor.fetchall()

    return [item[0] for item in rs]

def category_list(year):
    sql = """
        SELECT category, count(*)
        FROM snopes_set
        WHERE year(published_date) = '%s' 
        GROUP BY category
        ORDER BY count(*) desc limit 5 
        """%(year)

    cursor.execute(sql)
    rs = cursor.fetchall()

    return [item[0] for item in rs], [item[1] for item in rs]

def category_count_by_year(year, category):
    sql = """
        SELECT count(*)
        FROM snopes_set
        WHERE year(published_date) = '%s' and category = '%s' 
        GROUP BY category
        """%(year, category)

    cursor.execute(sql)
    rs = cursor.fetchall()
    
    if len(rs) == 0:
        return 0
    else :
        return rs[0][0]

def get_nouns(data):
    tagged_data = nltk.pos_tag(data)
    nouns = [word for word, pos in tagged_data \
        if (pos.startswith('N'))]
    return nouns

def frequency(title_list):
    frequency = {}
    
    for title in title_list:
        title = title.lower()

        #filter short and long wowrds
        common_words = ["for", "the", "and", "did", "was", "were", "does", "you", "from", "with", "are", "not", "his", "that", "this", "after", "during", "can"]
        match_pattern = re.findall(r'\b[a-z]{3,15}\b', title)

        #extract noun only 
        nouns = get_nouns(match_pattern)
        #print(nouns)
        for word in nouns:
        #for word in match_pattern:
            if word not in common_words:
                count = frequency.get(word, 0)
                frequency[word] = count + 1
    
    result = sorted(frequency.items(), key = operator.itemgetter(1))  
    result.reverse()
    '''
    try:
        for i in range(10):
            print('%s : %s'%(result[i][0], result[i][1]))
    except IndexError:
        print()
    '''
    return result[0:10]

if __name__ == '__main__':
    conn, cursor, = sql_connect()   
    
    #frequency(titles(2014, 12))
    #frequency(titles(2015, 7))
    #frequency(titles(2016, 1))
    #frequency(titles(2017, 4))
    #frequency(titles(2011,7))
    #for i in range(2011,2019):
    #    frequency(titles_year(i))
    categories = ["medical", "politics", "viral phenomena", "history", "science", "food"]
    years = ["2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018"]

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter('trending_keywords_year.xlsx', engine='xlsxwriter')
    #writer = pd.ExcelWriter('./trending_words/trending_keywords_year.xlsx', engine='xlsxwriter')
    dataframe_list = []
    for i in years[:-1]:
        year_data = []
        for j in range(1, 13):
            result = frequency(titles(i,j))
            year_data.append(result)
        df = pd.DataFrame(year_data, index = range(1, 13), columns = range(1,11))
        dataframe_list.append(df)
        #df.to_csv('./trending_words/%s.csv'%i, encoding='utf-8')

    for i, item in enumerate(dataframe_list):
        item.to_excel(writer, sheet_name=years[i])
    writer.save()

    category_data = []
    for item in categories:
        year_data = []
        year_value = []
        for i in range(2011, 2019):
            words = frequency(titles_year_category(i, item))
            word_list = []
            count_list = []
            for j in range(len(words)):
                word = words[j][0]
                count = words[j][1]
                word_list.append(word)
                count_list.append(count)
            year_data.append(word_list)
            year_value.append(count_list)
        #print(year_data)
        category_data.append(year_data)
        #df = pd.DataFrame(category_data, index = range(1, 11), columns = years)
        df = pd.DataFrame(year_data, index = range(2011, 2019), columns = range(1, 11))
        df.to_csv('./trending_words/%s.csv'%item, encoding='utf-8')

        #backdata
        df = pd.DataFrame(year_value, index = range(2011, 2019), columns = range(1, 11))
        df.to_csv('./trending_words/%s_data.csv'%item, encoding='utf-8')


    #top 10 categories in a year
    #make one total list 
    category_all = []
    for i in range(2011, 2019):
        categories, values = category_list(i)

        for item in categories:
            if item not in category_all:
                category_all.append(item)

    category_count = []
    for c in category_all:
        count_list = []
        for i in range(2011, 2018):
            count = category_count_by_year(i, c)
            count_list.append(count)
        category_count.append(count_list)
    #print(category_count)
    df = pd.DataFrame(category_count, index = category_all, columns = range(2011, 2018))
    #print(df)
    
    LinePlt = LinePlot()
    LinePlt.set_label('year', 'number of articles')
    LinePlt.set_plot_data(category_count, 'category count')
    LinePlt.set_xticks(range(2011, 2018))
    LinePlt.set_legends(category_all)
    LinePlt.save_image('./image/category_count_year.png')
    sql_close(cursor, conn)

    


