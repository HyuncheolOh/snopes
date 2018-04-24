import numpy as np
import MySQLdb
import nltk
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

def get_politifact_data():
    conn, cursor, = sql_connect()

    sql = """
        SELECT title, veracity 
        FROM other_data
        """

    cursor.execute(sql)
    rs = cursor.fetchall()

    claim = [item[0] for item in rs]
    veracity_list = [item[1] for item in rs]

    _X, y = embed_words(claim, veracity_list, 41)

    sql_close(cursor, conn)
    return _X, y

def get_claim_veracity_2018():
    conn, cursor, = sql_connect()

    sql = """
        SELECT claim, veracity
        FROM snopes_set 
        WHERE (veracity = 'true' or veracity = 'false') and (claim != 'None' and claim != '') 
        and (category = 'Fake News' or category = 'Politics' or category = 'Politicians')
    """
    
        #WHERE (veracity = 'true' or veracity = 'false') and (claim != 'None' and claim != '') and published_date >= '2018-01-01'
        #WHERE (veracity = 'true' or veracity = 'false') and claim != '' and published_date >= '1995-01-01' 
    cursor.execute(sql)
    rs = cursor.fetchall()

    x = [item[0] for item in rs]
    y = [item[1] for item in rs]
    _X, y = embed_words(x, y, 41)
    
    sql_close(cursor, conn)
    
    return _X, y 

def get_claim_veracity():
    conn, cursor, = sql_connect()

    sql = """
        SELECT claim, veracity
        FROM snopes_set 
        WHERE (veracity = 'true' or veracity = 'false') and (claim != '' and claim != 'None')
    """

    #WHERE (veracity = 'true' or veracity = 'false') and claim != '' and published_date >= '1995-01-01' 
    cursor.execute(sql)
    rs = cursor.fetchall()

    x = [item[0] for item in rs]
    y = [item[1] for item in rs]
    _X, y = embed_words(x, y)
    
    sql_close(cursor, conn)
    
    return _X, y 

def embed_words(x, veracity_list, max_length=-1):
    tokenizer = RegexpTokenizer(r'\w+')

    sentences = []    
    stop_words = set(stopwords.words('english'))
    for item in x:
        word_tokens = tokenizer.tokenize(item.lower())
        #stopwords remove
        word_tokens = [w for w in word_tokens if not w in stop_words]
        sentences.append(word_tokens)
    
    y = []
    for item in veracity_list:
        y.append(np.array([convert_veracity(item)]))

    from gensim.models import Word2Vec

    model = Word2Vec(sentences, min_count = 1)

    #convert sentence to embedded vectors
    x = [] 
    
    for word_tokens in sentences:
        word_index = []
        for word in word_tokens:
            word_index.append(model[word])
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

def batch_iter(data, batch_size, num_epochs, shuffle=True):
    """Iterate the data batch by batch"""
    data = np.array(data)
    data_size = len(data)
    num_batches_per_epoch = int(data_size / batch_size) + 1

    for epoch in range(num_epochs):
	if shuffle:
            shuffle_indices = np.random.permutation(np.arange(data_size))
	    shuffled_data = data[shuffle_indices]
	else:
	    shuffled_data = data

	for batch_num in range(num_batches_per_epoch):
	    start_index = batch_num * batch_size
	    end_index = min((batch_num + 1) * batch_size, data_size)
	    yield shuffled_data[start_index:end_index]
  
if __name__ == '__main__':
    get_claim_veracity()
    get_politifact_data()
