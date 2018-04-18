#############################################
# distribution of articles depends on word count 
# proper noun distribution
#############################################

from __future__ import print_function
import MySQLdb 
import json
import codecs
import ast
import nltk
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

def sql_connect():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="fake_news", use_unicode=True, charset='utf8')
    cursor = conn.cursor()
    return conn, cursor

def sql_close(cursor, conn):
    cursor.close()
    conn.close()

def data_trim(data):
    data = data.replace('"', '\\"')
    return data

def get_nouns_verbs(data):
    tagged_data = nltk.pos_tag(data)
    verbs = [word for word, pos in tagged_data \
            if (pos.startswith('V') or pos.startswith('N'))]
    return verbs

def is_contain_proper_noun(data):
    tagged_data = nltk.pos_tag(data)
    #if ("NNP" or "NNPS" in pos for word, pos in tagged_data):
    print(tagged_data)
    result = [pos for word, pos in tagged_data if "NNP" in pos]
    if len(result) > 0:
        return True
    else :
        return False



if __name__ == '__main__':
    import sys
    conn, cursor, = sql_connect()

    sql = """
        SELECT post_id, title, veracity, share_count, claim, sources 
        FROM snopes_set
        """
    cursor.execute(sql)
    rs = cursor.fetchall()
    count = 0
    word_count = np.zeros((25), dtype='int32')
    max_word = 0
    for item in rs:
        post_id, title, veracity, share_count, claim, source, = item

        print(post_id)
        tokenizer = RegexpTokenizer(r'\w+')
        word_tokens = tokenizer.tokenize(title.lower())

        #stopwords remove
        stop_words = set(stopwords.words('english'))
        word_tokens = [w for w in word_tokens if not w in stop_words]

        #extract nouns and verbs
        #word_tokens = get_nouns_verbs(word_tokens)

        word_length = len(word_tokens)
        word_count[word_length] += 1
        if word_length > max_word:
            max_word = word_length

        #print(title)
        #is_contain_proper_noun(word_tokens)
        #extract sentence and words based on the word count
        
        
        _wc = 6 
        if word_length == _wc:
            print(title)
            is_contain_proper_noun(word_tokens)
            
            for i in range(word_length):
#                print(word_tokens[i]) 
                sys.stdout.write(word_tokens[i])
                if i != _wc-1:
                    sys.stdout.write(', ')
            sys.stdout.write("\n")

            word_tokens = get_nouns_verbs(word_tokens)
            for i in range(len(word_tokens)):
                sys.stdout.write(word_tokens[i])
                if i != len(word_tokens)-1:
                    sys.stdout.write(', ')
            sys.stdout.write('\n')
            count += 1
            if count >= 10:
                break
        
        sys.stdout.flush()
        
    

    word = word_count[:max_word+1]
    for i in range(len(word_count)):
        print(word_count[i])
    sql_close(cursor, conn)




