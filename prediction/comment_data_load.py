import numpy as np
import MySQLdb


import json
from Queue import Queue
import nltk
import util_sampling as sampling
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer


def sql_connect():
  conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="reddit_news")
  cursor = conn.cursor()
  return conn, cursor


def sql_close(cursor, conn):
  cursor.close()
  conn.close()


def get_data():
  conn, cursor, = sql_connect()
  sql = """
    SELECT body, least(calc_width, 1)
    FROM comments
    WHERE depth = '8'
    limit 10000
    """
  cursor.execute(sql)
  rs = cursor.fetchall()
  print("sql query done")

  terminal_count = 0
  total_count = 0
  x = []
  y = []
  for item in rs:
    body, has_child, = item
    x.append(body)
    y.append([has_child])

  tokenizer = RegexpTokenizer(r'\w+')

  sentences = []    
  stop_words = set(stopwords.words('english'))
  for item in x:
      word_tokens = tokenizer.tokenize(item.lower())
      #stopwords remove
      word_tokens = [w for w in word_tokens if not w in stop_words]
      sentences.append(word_tokens)

  from gensim.models import Word2Vec

  model = Word2Vec(sentences, min_count = 1)
 
  x = []
   
  for word_tokens in sentences:
      word_index = []
      
      for i, word in enumerate(word_tokens):
      #    if i == 100:
      #        break
          word_index.append(model[word])
      a = np.array(word_index)
      x.append(np.array(word_index))
  X = np.array(x)
  y = np.array(y)
  max_length = len(max(X, key=len))
  _X = []
  
  for i in range(len(X)):
    if len(X[i]) != max_length:
        x_length = len(X[i])
        if x_length == 0:
            X[i] = np.zeros(shape=(max_length, 100))
        else : 
            X[i] = np.concatenate((X[i], np.zeros(shape=(max_length - x_length, 100))), axis=0)
#        for j in range(max_length - x_length) :
#            X[i] = np.concatenate((X[i], np.zeros(shape=(1, 100))), axis=0)
        _X.append(X[i])
    else :
        _X.append(X[i])
  _X = np.array(_X)
  y = np.array(y)
  print("word2vec done")

  #data = {}
  #data['body'] = _X.tolist()
  #data['label'] = y.tolist()
  #json.dump(data, open('../data/comments.body.json', 'w')) 
  #print("json dump done")
  sql_close(cursor, conn)
  return _X, y

if __name__ == '__main__':
  import sys, os


  get_data()
  
