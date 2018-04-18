import MySQLdb
import csv
import sys
import codecs
from sklearn.model_selection import train_test_split

MAX_COUNT = 10000


def load_data(folder_name):
    import os
    print("load_data")
    # check folder exists or not
    folder_name="testdata"
    if os.path.exists(folder_name + "/news_data.csv"):
        # rawdata = pandas.read_csv(folder_name+"/reddit_post.csv", names=['key', 'title', 'vader'])
        f = codecs.open(folder_name + "/news_data.csv", "r", "latin1");

        X = []
        y = []
        count = 0
        for line in f.readlines():
            count += 1
            if count ==1:
                continue
         #   print(line)
            #line.rstrip("\n")
            split_v = line.split(',')
            X.append(split_v[11] + split_v[14])
            y.append(positivity(split_v[5]))
#            print(X)
#            break
#            if count > 100:
#                break
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)
        return X_train, X_test, y_train, y_test

#convert positivity 1(positive), 0(neutral), -1(negative)
def positivity(value):
    try:
        int_val = int(value)
        if int_val > 5:
            return 1
        else:
            return 0 
    except:
        return 0



if __name__ == '__main__':
    load_data("testdata")
