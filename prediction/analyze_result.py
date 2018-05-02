import MySQLdb

from operator import itemgetter

from sklearn.metrics import *


def accuracy_per_depth(y_true, y_pred):
  diff = 0
  for seq_t, seq_p in zip(y_true, y_pred):
    for t, p in zip(seq_t, seq_p):
      if t != round(p):
        diff += 1

  return float(diff)/len(y_true)
 



def analyze():
  import sys, os

  path = './result'

  files = os.listdir(path)

  for fname in files:
    if fname[-3:] != 'tsv':
      continue
    
    if len(sys.argv) > 1:
      fname = sys.argv[1]

    f = open('%s/%s'%(path, fname), 'r')
    acc = f.readline().replace('\n', '')

    print fname, acc

    results = []
    acc_depth = []

    for line in f:
      splits = line.replace('\n', '').split('\t')
      sub_result = map(lambda x:x.split(','), splits)
      results.append(sub_result)
    f.close()

    _y_true = map(itemgetter(0), results)
    _y_pred = map(itemgetter(1), results)

    for depth, result in enumerate(zip(zip(*_y_true), zip(*_y_pred))):
      y_true, y_pred, = result
      y_true_int = map(int, y_true)
      y_pred_int = map(int, y_pred)

      accuracy = accuracy_score(y_true_int, y_pred_int)
      precision = precision_score(y_true_int, y_pred_int)
      recall = recall_score(y_true_int, y_pred_int)
      f1 = f1_score(y_true_int, y_pred_int)
      #print depth, precision_recall_fscore_support(map(int, y_true), map(int, y_pred))
      print accuracy, precision, recall, f1
  
      """
      correct = 0
      for element_true, element_pred in zip(y_true, y_pred):
        if element_true == element_pred:
          correct += 1

      #print depth, '%.4f'%(float(correct)/len(y_true))
      acc_depth.append('%.4f'%(float(correct)/len(y_true)))
      """
      
    
if __name__=='__main__':
    analyze()
