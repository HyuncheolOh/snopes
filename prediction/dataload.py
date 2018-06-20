import numpy as np
import MySQLdb
import nltk
import re
import util_sampling as sampling
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

#sql connect
def sql_connect():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="fake_news", use_unicode=True, charset='utf8')
    cursor = conn.cursor()
    return conn, cursor

#sql close
def sql_close(cursor, conn):
    cursor.close()
    conn.close()

def convert_veracity(veracity):
    if 'true' in veracity.lower():
        return 1
    elif 'false' in  veracity.lower():
        return 0
    elif 'mixture' in veracity.lower():
        return 2

def convert_date(year):
    # 200701 --> 200701 0 0 0 0 0 
    print(year)
    item_list = []
    for item in year:
        temp = [item] + [0] * 99 
        temp = map(int, temp)
        temp = np.array(temp)
        item_list.append(temp)
    
    item_list = np.array(item_list)
    print(item_list.shape)
    return item_list

def date_onehot(year):
    from numpy import array
    from numpy import argmax
    from sklearn.preprocessing import LabelEncoder
    from sklearn.preprocessing import OneHotEncoder
    months = [item[4:] for item in year]
    months = map(int, months)
    years = [item[:4] for item in year]
    values = array(years)
    
    # integer encode
    label_encoder = LabelEncoder()
    integer_encoded = label_encoder.fit_transform(values)
    #print(integer_encoded)
    max_length = 100
    encoded_length = max(integer_encoded)
    # binary encode
    onehot_encoder = OneHotEncoder(sparse=False)
    integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
    #integer_encoded = integer_encoded.reshape(size, 1)
    onehot_encoded = onehot_encoder.fit_transform(integer_encoded)

    for i, item in enumerate(months):
        onehot_encoded[i] = item * onehot_encoded[i]

    new_list = []
    for i in range(len(onehot_encoded)):
        new_list.append(np.pad(onehot_encoded[i], (0, max_length - encoded_length-1), 'constant'))

#    print(onehot_encoded)
    return np.array(new_list)



def get_onehot(year):
    from numpy import array
    from numpy import argmax
    from sklearn.preprocessing import LabelEncoder
    from sklearn.preprocessing import OneHotEncoder

    #print(values)
    # integer encode
    label_encoder = LabelEncoder()
    integer_encoded = label_encoder.fit_transform(values)
    #print(integer_encoded)
    max_length = 100
    encoded_length = max(integer_encoded)
    # binary encode
    onehot_encoder = OneHotEncoder(sparse=False)
    integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
    #integer_encoded = integer_encoded.reshape(size, 1)
    onehot_encoded = onehot_encoder.fit_transform(integer_encoded)
    new_list = []
    for i in range(len(onehot_encoded)):
        new_list.append(np.pad(onehot_encoded[i], (0, max_length - encoded_length-1), 'constant'))
#    print(onehot_encoded)
    #print(np.array(new_list))
    return np.array(new_list)



def get_onehot(year):
    from numpy import array
    from numpy import argmax
    from sklearn.preprocessing import LabelEncoder
    from sklearn.preprocessing import OneHotEncoder

    values = array(year)
    #print(values)
    # integer encode
    label_encoder = LabelEncoder()
    integer_encoded = label_encoder.fit_transform(values)
    #print(integer_encoded)
    max_length = 100
    encoded_length = max(integer_encoded)
    # binary encode
    onehot_encoder = OneHotEncoder(sparse=False)
    integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
    #integer_encoded = integer_encoded.reshape(size, 1)
    onehot_encoded = onehot_encoder.fit_transform(integer_encoded)
    new_list = []
    for i in range(len(onehot_encoded)):
        new_list.append(np.pad(onehot_encoded[i], (0, max_length - encoded_length-1), 'constant'))
#    print(onehot_encoded)
    #print(np.array(new_list))
    return np.array(new_list)

def clean_str(s):
    """Clean sentence"""
    s = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", s)
    s = re.sub(r"\'s", " \'s", s)
    s = re.sub(r"\'ve", " \'ve", s)
    s = re.sub(r"n\'t", " n\'t", s)
    s = re.sub(r"\'re", " \'re", s)
    s = re.sub(r"\'d", " \'d", s)
    s = re.sub(r"\'ll", " \'ll", s)
    s = re.sub(r",", " , ", s)
    s = re.sub(r"!", " ! ", s)
    s = re.sub(r"\(", " \( ", s)
    s = re.sub(r"\)", " \) ", s)
    s = re.sub(r"\?", " \? ", s)
    s = re.sub(r"\s{2,}", " ", s)
    s = re.sub(r'\S*(x{2,}|X{2,})\S*',"xxx", s)
    s = re.sub(r'[^\x00-\x7F]+', "", s)
    return s.strip().lower()

def get_emergent_data(year):
    print(year)
    conn, cursor, = sql_connect()

    sql = """
        SELECT title, veracity, date_format(dates, '%Y%m')
        FROM other_data
        WHERE source = 'emergent' and (year(dates) = {0})
        ORDER BY rand()
        """

    sql = sql.format(year)
    cursor.execute(sql)
    rs = cursor.fetchall()

    claim = [item[0] for item in rs]
    veracity_list = [item[1] for item in rs]
    date = [item[2] for item in rs]

    _X, y = embed_words(claim, veracity_list)
    
    #date onehot add
    date = get_onehot(date)
    date = np.reshape(date, (-1, 1, 100))
    _X = np.concatenate((date, _X), axis=1)
   
    sql_close(cursor, conn)
    return _X, y


def get_politifact_data(year):
    print(year)
    conn, cursor, = sql_connect()

    sql = """
        SELECT title, veracity, date_format(dates, '%Y%m')
        FROM other_data
        WHERE source = 'politifact' 
        ORDER BY rand()
        """

    sql = sql.format(year)
    cursor.execute(sql)
    rs = cursor.fetchall()

    claim = [item[0] for item in rs]
    veracity_list = [item[1] for item in rs]
    date = [item[2] for item in rs]

    _X, y = embed_words(claim, veracity_list, 100)
    
    #date onehot add
    #date = get_onehot(date)
    #date = np.reshape(date, (-1, 1, 100))
    #_X = np.concatenate((date, _X), axis=1)
   
    sql_close(cursor, conn)
    return _X, y

    #return claim, veracity_list, date

def get_snopes_politics(year):
    print(year)
    conn, cursor, = sql_connect()

    sql = """
        SELECT claim, veracity, date_format(published_date, '%Y%m')
        FROM snopes_set 
        WHERE (veracity = 'true' or veracity = 'false') and (claim != '' and claim != 'None') and (category = 'politics' or category = 'politicians')
    """

        #WHERE (veracity = 'true' or veracity = 'false') and (claim != '' and claim != 'None') and (category = 'politics' or category = 'politicians'))
    sql = sql.format(year, (int(year)-3))
    cursor.execute(sql)
    rs = cursor.fetchall()

    x = [item[0] for item in rs]
    y = [item[1] for item in rs]
    date = [item[2] for item in rs]
    _X, y = embed_words(x, y)
    
    sql_close(cursor, conn)
 
    #date onehot add
    #date = get_onehot(date)
    #date = np.reshape(date, (-1, 1, 100))
    #_X = np.concatenate((date, _X), axis=1)

   
    return _X, y 

def get_snopes_data_category(category):
    print(category)
    conn, cursor, = sql_connect()

    sql = """
        SELECT claim, veracity, category, description, title, tag, date_format(published_date, '%Y%m')
        FROM snopes_set 
        WHERE (veracity = 'true' or veracity = 'false') and (claim != '' and claim != 'None') and ({0})
    """
    cg = ["Fauxtography", "Politics", "Inboxer Rebellion", "Politicians", "Business", "Crime", "Medical", "Entertainment", "Media Matters", "Critter Country"]

    categories = category.split(",")
    if len(categories) == 1:
        sql = sql.format("category = '%s'"%categories[0])
    else:
        c_list = ["category = '%s'"%item for item in categories]
        condition = " or ".join(c_list)
        print(condition)
        sql = sql.format(condition)

    print(sql)
    #sql = sql.format(cg[5], cg[6], cg[7], cg[8], cg[9])
    #SELECT claim, veracity, category, description, title, tag, date_format(published_date, '%Y%m')
    #WHERE (veracity = 'true' or veracity = 'false') and (claim != '' and claim != 'None') and (category != 'fake news' and category = '{0}' or category = '{1}' or category = '{2}' or category = '{3}' or category = '{4}');
    cursor.execute(sql)
    rs = cursor.fetchall()

    x = [item[0] for item in rs]
    y = [item[1] for item in rs]
    c = [item[2] for item in rs]
    d = [item[3] for item in rs]
    t = [item[4] for item in rs]
    tag = [item[5] for item in rs]
    date = [item[6] for item in rs]
    #x = [a + ' ' + b for a, b in zip(x, tag)]
    
    #claim, veracity, dates = get_politifact_data()
    #x = x + claim
    #y = y + veracity
    #date = date + dates
    #c = c + ['other'] * len(claim)
    
    _X, y = embed_words(x, y, 100)

    #date onehot add
    #date = get_onehot(date)
    #date = np.reshape(date, (-1, 1, 100))
    #_X = np.concatenate((date, _X), axis=1)

    #category data add 
    c = get_onehot(c)
    c = np.reshape(c, (-1, 1, 100))
    _X = np.concatenate((c, _X), axis=1)
    sql_close(cursor, conn)
   
    return _X, y


def get_snopes_data(year):
    print(year)
    conn, cursor, = sql_connect()

    sql = """
        SELECT claim, veracity, category, description, title, tag, date_format(published_date, '%Y%m')
        FROM snopes_set 
        WHERE (veracity = 'true' or veracity = 'false') and (claim != '' and claim != 'None') and (category != 'fake news');
    """
        #WHERE (veracity = 'true' or veracity = 'false') and (claim != '' and claim != 'None') and category != 'fake news';
    cg = ["Fauxtography", "Politics", "Inboxer Rebellion", "Politicians", "Business", "Crime", "Medical", "Entertainment", "Media Matters", "Critter Country"]
    #sql = sql.format(cg[0], cg[1], cg[2], cg[3], cg[4])
    sql = sql.format(year)
    cursor.execute(sql)
    rs = cursor.fetchall()

    x = [item[0] for item in rs]
    y = [item[1] for item in rs]
    c = [item[2] for item in rs]
    d = [item[3] for item in rs]
    t = [item[4] for item in rs]
    tag = [item[5] for item in rs]
    date = [item[6] for item in rs]
    #x = [a + ' ' + b for a, b in zip(x, tag)]
    
    #claim, veracity, dates = get_politifact_data()
    #x = x + claim
    #y = y + veracity
    #date = date + dates
    #c = c + ['other'] * len(claim)
    
    _X, y = embed_words(x, y)

    #date onehot add
    #date = get_onehot(date)
    #date = np.reshape(date, (-1, 1, 100))
    #_X = np.concatenate((date, _X), axis=1)
   
    #category data add 
    c = get_onehot(c)
    c = np.reshape(c, (-1, 1, 100))
    #_X = np.concatenate((c, _X), axis=1)
    sql_close(cursor, conn)
    
    return _X, y 

def get_snopes_data_with_c(year):
    print(year)
    conn, cursor, = sql_connect()

    sql = """
        SELECT claim, veracity, category, description, title, tag, date_format(published_date, '%Y%m')
        FROM snopes_set 
        WHERE (veracity = 'true' or veracity = 'false') and (claim != '' and claim != 'None') and (category != 'fake news');
    """
        #WHERE (veracity = 'true' or veracity = 'false') and (claim != '' and claim != 'None') and category != 'fake news';
    cg = ["Fauxtography", "Politics", "Inboxer Rebellion", "Politicians", "Business", "Crime", "Medical", "Entertainment", "Media Matters", "Critter Country"]
    
    year = year.split(",")
    if len(year) == 1:
        sql = sql.format("year(published_date) = %s"%year[0])
    else:
        c_list = ["year(published_date) = %s"%item for item in year]
        condition = " or ".join(c_list)
        print(condition)
        sql = sql.format(condition)


    #sql = sql.format(cg[0], cg[1], cg[2], cg[3], cg[4])
    sql = sql.format(year)
    cursor.execute(sql)
    rs = cursor.fetchall()

    x = [item[0] for item in rs]
    y = [item[1] for item in rs]
    c = [item[2] for item in rs]
    d = [item[3] for item in rs]
    t = [item[4] for item in rs]
    tag = [item[5] for item in rs]
    date = [item[6] for item in rs]
    #x = [a + ' ' + b for a, b in zip(x, tag)]
    
    #claim, veracity, dates = get_politifact_data()
    #x = x + claim
    #y = y + veracity
    #date = date + dates
    #c = c + ['other'] * len(claim)
    
    _X, y = embed_words(x, y)

    #date onehot add
    #date = get_onehot(date)
    #date = np.reshape(date, (-1, 1, 100))
    #_X = np.concatenate((date, _X), axis=1)
   
    #category data add 
    c = get_onehot(c)
    c = np.reshape(c, (-1, 1, 100))
    _X = np.concatenate((c, _X), axis=1)
    sql_close(cursor, conn)
    
    return _X, y 

def embed_words(x, veracity_list, max_length=-1):
    tokenizer = RegexpTokenizer(r'\w+')

    sentences = []    
    stop_words = set(stopwords.words('english'))
    for item in x:
        word_tokens = tokenizer.tokenize(clean_str(item))
        #word_tokens = tokenizer.tokenize(item.lower())
        #stopwords remove
        #word_tokens = [w for w in word_tokens if not w in stop_words]
        sentences.append(word_tokens)
    
    y = []
    for item in veracity_list:
        y.append(np.array([convert_veracity(item)]))

    from gensim.models import Word2Vec

    #model = Word2Vec(sentences, min_count = 1)
    model = Word2Vec(sentences)

    #convert sentence to embedded vectors
    x = [] 
     
    for word_tokens in sentences:
        word_index = []
        for word in word_tokens:
            try :
                word_index.append(model[word])
            except KeyError as e:
                print()
        a = np.array(word_index)
        x.append(np.array(word_index))

    X = np.array(x)
    y = np.array(y)
    if max_length == -1:
        max_length = len(max(X, key=len))
    print("snopes max ", max_length)
    _X = []
    for i in range(len(X)):
      if len(X[i]) != max_length:
          x_length = len(X[i])
          if x_length == 0:
              X[i] = np.zeros(shape=(max_length, 100))
          else : 
              X[i] = np.concatenate((X[i], np.zeros(shape=(max_length - x_length, 100))), axis=0)
#          for j in range(max_length - x_length) :
#              X[i] = np.concatenate((X[i], np.zeros(shape=(1, 100))), axis=0)
          _X.append(X[i])
      else :
          _X.append(X[i])
    _X = np.array(_X)
    y = np.array(y)

    return _X, y 


if __name__ == '__main__':
    #get_claim_veracity()
    #get_claim_veracity_2018()
    #get_politifact_data()
    #get_snopes_politics()
    #get_category_onehot()
    #get_snopes_data(2017)
    #get_claim_veracity()
    #get_politifact_data()
    get_snopes_data_category('Politics')                                                   

