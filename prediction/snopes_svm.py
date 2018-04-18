import numpy as np
import json
import MySQLdb

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score

#sql connect
def sql_connect():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="fake_news", use_unicode=True, charset='utf8')
    cursor = conn.cursor()
    return conn, cursor

#sql close
def sql_close(cursor, conn):
    cursor.close()
    conn.close()

def categories():
    sql = """
        SELECT category
        FROM snopes_set
        GROUP BY category
        """
    
    cursor.execute(sql)
    rs = cursor.fetchall()

    return [item[0] for item in rs]

def fact_checker_list():
    sql = """
        SELECT fact_checker
        FROM snopes_set
        GROUP BY fact_checker
        """
    
    cursor.execute(sql)
    rs = cursor.fetchall()

    return [item[0] for item in rs]

def source_num(sources_json):
    if sources_json == '"None"' or sources_json == None:
        return 0
    else :
        return len(json.loads(sources_json))

def convert_date(published_date):
    if published_date == None:
        return 0
    return published_date.strftime('%Y%m%d')

def convert_veracity(veracity):
    if 'true' in veracity.lower():
        return 1
    elif 'false' in  veracity.lower():
        return 0

def convert_fact_checker(item_list, item):
    try :
        return item_list.index(item)
    except ValueError:
        return -1

def get_features():
    conn, cursor, = sql_connect()

    sql = """
        SELECT post_id, category, published_date, share_count, fact_checker, sources_json, veracity
        FROM snopes_set
        WHERE (veracity = 'True' or veracity = 'False') and claim != ''
        ORDER BY post_id
        """

    cursor.execute(sql)
    rs = cursor.fetchall()

    category_list = categories()
    factchecker_list = fact_checker_list()

    true_num = 0; false_num = 0;
    x = []
    for item in rs:
        post_id, category, published_date, share_count, fact_checker, sources_json, veracity ,= item
        x.append([category_list.index(category), convert_date(published_date), share_count, convert_fact_checker(factchecker_list, fact_checker), source_num(sources_json)])
    
    sql_close(cursor, conn)
    return x

def get_features_and_predict():
    sql = """
        SELECT post_id, category, published_date, share_count, fact_checker, sources_json, veracity
        FROM snopes_set
        WHERE (veracity = 'True' or veracity = 'False') 
        """

    cursor.execute(sql)
    rs = cursor.fetchall()

    category_list = categories()
    factchecker_list = fact_checker_list()

    true_num = 0; false_num = 0;
    x = []; y = []
    for item in rs:
        post_id, category, published_date, share_count, fact_checker, sources_json, veracity ,= item
        x.append([category_list.index(category), convert_date(published_date), share_count, convert_fact_checker(factchecker_list, fact_checker), source_num(sources_json)])
        y.append(convert_veracity(veracity))
        if convert_veracity(veracity) == 1:
            true_num += 1
        else : 
            false_num += 1

    print("true : %d, false : %d"%(true_num, false_num))

    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size = 0.33, random_state=42)

    clf = svm.SVC()
    clf.fit(X_train, y_train)
    result = clf.predict(X_test)
    for i, item in enumerate(result):
        print(item, y_test[i])
    print(y_train.count(1), y_train.count(0)) 
    print("accuracy : %s"%accuracy_score(result, y_test))
    print("precision : %s"%precision_score(result, y_test))
    print("recall : %s"%recall_score(result, y_test))
    print("f1 score : %s"%f1_score(result, y_test))

#    print(result)
    

def get_claims():
    conn, cursor, = sql_connect()
    
    sql = """
        SELECT claim, veracity
        FROM snopes_set
        WHERE claim != '' and (veracity = 'True' or veracity = 'False')
        ORDER BY post_id
        """

    cursor.execute(sql)
    rs = cursor.fetchall()

    sql_close(cursor, conn)
    return [item[0] for item in rs], [item[1] for item in rs]

def predict_claim():
    claim_list, veracity_list = get_claims()
   
    tokenizer = RegexpTokenizer(r'\w+')
    stop_words = set(stopwords.words('english'))
    sentences = []    
    for item in claim_list:
        word_tokens = tokenizer.tokenize(item.lower())

        #stopwords remove
        word_tokens = [w for w in word_tokens if not w in stop_words]
        sentences.append(' '.join(word_tokens))

    y = []
    for item in veracity_list:
        y.append(convert_veracity(item))

    return train_test_split(sentences, y, test_size = 0.33, random_state=42)
    #X_train, X_test, y_train, y_test = train_test_split(sentences, y, test_size = 0.33, random_state=42)

    '''
    print("accuracy : %s"%accuracy_score(result, y_test))
    print("precision : %s"%precision_score(result, y_test))
    print("recall : %s"%recall_score(result, y_test))
    print("f1 score : %s"%f1_score(result, y_test))
    '''
def evaluate(_y, y):
    print("accuracy : %s"%accuracy_score(_y, y))
    print("precision : %s"%precision_score(_y, y))
    print("recall : %s"%recall_score(_y, y))
    print("f1 score : %s"%f1_score(_y, y))


if __name__ == "__main__":

    #numberof articles 
    total_count = 0

    #sql connect
    conn, cursor, = sql_connect()
    predict_claim()    
#    get_features()
