import sys
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from itertools import cycle
from operator import itemgetter
from sklearn import svm, datasets
from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import label_binarize
from sklearn.multiclass import OneVsRestClassifier
from scipy import interp


def roc(input_file, filename):
    path = './result/result.%s.tsv'%input_file

    results = []
    with open(path, 'r') as f:
        acc= f.readline().replace('\n', '')
        for line in f:
            splits = line.replace('\n', '').split('\t')
            sub_result = map(lambda x:x.split(','), splits)
            results.append(sub_result)

    y_true = map(itemgetter(0), results)
    y_pred = map(itemgetter(1), results)
    y_test = [map(int, y) for y in y_true]
    y_score = [map(int, y) for y in y_pred]
    # Compute ROC curve and ROC area for each class
    #y_test = np.array([1, 1, 1, 1, 0, 0])
    #y_score = np.array([0.9, 0.9, 0.9, 0.1, 0.1, 0.1])
    fpr, tpr, thresholds = roc_curve(y_test, y_score)
    print(fpr)
    print(tpr)
    roc_auc = auc(fpr, tpr)
    thresholds
    print("auc : %s"%roc_auc)
    fig = plt.figure()
    lw = 2
    plt.plot(fpr, tpr, color='darkorange',
                     lw=lw, label='ROC curve (area = %0.2f)' % roc_auc)
    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic')
    plt.legend(loc="lower right")
    plt.savefig('./auc/%s'%filename)

if __name__ == "__main__":
    input_file = ""
    filename = "rocline"

    input_file = sys.argv[1]
    filename = sys.argv[2]
    roc(input_file, filename)
