""" Convolutional Neural Network.

Build and train a convolutional neural network with TensorFlow.
This example is using the MNIST database of handwritten digits
(http://yann.lecun.com/exdb/mnist/)

Author: Aymeric Damien
Project: https://github.com/aymericdamien/TensorFlow-Examples/
"""

from __future__ import division, print_function, absolute_import

import tensorflow as tf
import dataload
import numpy as np
import sys
import os
import util_sampling as sampling
from sklearn.model_selection import train_test_split
from tensorflow import flags

# Import MNIST data
#from tensorflow.examples.tutorials.mnist import input_data
#mnist = input_data.read_data_sets("/tmp/data/", one_hot=True)

class ToySequenceData(object):
    def __init__(self, X, y, max_length):
        self.data = []
        self.labels = [] #one hot [1.0, 0.0]
        self.seqlen = []
        self.batch_id = 0
        seq_max_len = max_length
        
        for i in range(len(X)):
            length = np.count_nonzero(X[i])
            #self.seqlen.append(length)
            #if x_length != max_length:
            #    for j in range(max_length - x_length):
            #        X[i].append([0] * 100)
            self.data.append(X[i])         
            y_val = lambda x : [1., 0.] if x == 1 else [0., 1.]
            self.labels.append(y_val(y[i]))

        self.seqlen = map(lambda x: np.count_nonzero(x)/100, X)

        print("sequence length 0 : " , self.seqlen.count(0))


    def next(self, batch_size):
        """ Return a batch of data. When dataset end is reached, start over.
        """
        if self.batch_id == len(self.data):
            self.batch_id = 0
        batch_data = (self.data[self.batch_id:min(self.batch_id +
                                                  batch_size, len(self.data))])
        batch_labels = (self.labels[self.batch_id:min(self.batch_id +
                                                      batch_size, len(self.data))])
        batch_seqlen = (self.seqlen[self.batch_id:min(self.batch_id +
                                                      batch_size, len(self.data))])
        self.batch_id = min(self.batch_id + batch_size, len(self.data))
        return batch_data, batch_labels, batch_seqlen

# Model
arg_num = len(sys.argv)
model_name = None
model_path = None
if (arg_num > 1):
    model_name = sys.argv[1]
    model_path  = os.path.abspath(os.path.join(os.path.curdir, "model/%s/%s.ckpt"%(model_name, model_name)))

print("model path : %s"%model_path)
arg = sys.argv[2]
#data load 
#_X, _y = dataload.get_claim_veracity()
#_X, _y = dataload.get_snopes_politics(arg)
#_X, _y = dataload.get_politifact_data(arg)
#_X, _y = dataload.get_snopes_data()
_X, _y = dataload.get_snopes_data_category(arg)
max_length = len(max(_X, key=len))
print("max length : %d"%max_length)
print("After sampling. Test data - non-zero : %s, total : %s"%(np.count_nonzero(_y), len(_y)))
flags.DEFINE_string("filter_sizes", "3,4,5", "Comma-separated filter sizes (default: '3,4,5')")
flags.DEFINE_integer("num_filters", 128, "Number of filters per filter size (default: 128)")
FLAGS = tf.flags.FLAGS
FLAGS._parse_flags()
testset = ToySequenceData(_X, _y, max_length)
# Training Parameters
learning_rate = 0.01
epoch =  100
batch_size = 100 
display_step = 100
embedding_size = 100
# Network Parameters
num_input = 784 # MNIST data input (img shape: 28*28)
num_classes = 2 # MNIST total classes (0-9 digits)
dropout = 0.5 # Dropout, probability to keep units
l2_reg_lambda = 0.1
# tf Graph input
#X = tf.placeholder(tf.float32, [None, num_input])
X = tf.placeholder(tf.float32, [None, max_length,  embedding_size])
Y = tf.placeholder(tf.float32, [None, num_classes])
keep_prob = tf.placeholder(tf.float32) # dropout (keep probability)

# Create model
class TextCNN(object):

    def __init__(self, x, y, dropout):
            l2_loss = tf.constant(0.0)
            num_filters = FLAGS.num_filters
            filter_sizes = FLAGS.filter_sizes
            sequence_length=max_length
            x = tf.reshape(x, shape=[-1, sequence_length, 100, 1])
            pooled_outputs = []
            filter_size = list(map(int, filter_sizes.split(",")))
            for i , f in enumerate(filter_size):
            
                with tf.name_scope("conv-maxpool-%s" % f):
                        filter_shape = [f, embedding_size, 1, num_filters]
                        W = tf.Variable(tf.truncated_normal(filter_shape, stddev = 0.1), name="W")
                        b = tf.Variable(tf.constant(0.1, shape=[num_filters]), name = "b")
                        conv = tf.nn.conv2d(x, W, strides=[1,1,1,1], padding="VALID", name="conv")
                        h = tf.nn.relu(tf.nn.bias_add(conv, b), name="relu")
                        pooled = tf.nn.max_pool(h, ksize=[1, sequence_length-f+1, 1, 1], strides=[1,1,1,1], padding="VALID", name="pool")
                        pooled_outputs.append(pooled)
            
            num_filters_total = num_filters * len(filter_size)
            pool = tf.concat(pooled_outputs, 3)
            pool_flat = tf.reshape(pool, [-1, num_filters_total])
            drop = tf.nn.dropout(pool_flat, dropout)
            
            with tf.name_scope("output"):
                W = tf.get_variable("W", shape=[num_filters_total, num_classes], initializer=tf.contrib.layers.xavier_initializer())
                b = tf.Variable(tf.constant(0.1, shape=[num_classes]), name="b")
                l2_loss += tf.nn.l2_loss(W)
                l2_loss += tf.nn.l2_loss(b)
                self.scores =tf.nn.xw_plus_b(drop, W, b, name="scores")
                self.predictions = tf.argmax(self.scores, 1, name="predictions")
    
            with tf.name_scope("loss"):
                losses = tf.nn.softmax_cross_entropy_with_logits(logits = self.scores, labels=y)
                self.loss = tf.reduce_mean(losses) + l2_reg_lambda * l2_loss

            with tf.name_scope("accuracy"):
                correct_predictions = tf.equal(self.predictions, tf.argmax(y, 1))
                self.accuracy = tf.reduce_mean(tf.cast(correct_predictions, "float"), name="accuracy")

# Construct model
cnn = TextCNN(X, Y, keep_prob)
#optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
#train_op = optimizer.minimize(cnn.loss)

global_step = tf.Variable(0, name="global_step", trainable=False)
optimizer = tf.train.AdamOptimizer(learning_rate)
grads_and_vars = optimizer.compute_gradients(cnn.loss)
train_op = optimizer.apply_gradients(grads_and_vars, global_step=global_step)


# Evaluate model
#correct_pred = tf.equal(tf.argmax(cnn.prediction, 1), tf.argmax(Y, 1))
#accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

# Initialize the variables (i.e. assign their default value)
init = tf.global_variables_initializer()
saver = tf.train.Saver()
# Start training
with tf.Session() as sess:

    # Run the initializer
    sess.run(init)

    saver.restore(sess, model_path)
    test_data = testset.data
    test_label = testset.labels
    # Calculate accuracy for 256 MNIST test images
#    print("Testing Accuracy:", sess.run(accuracy, feed_dict={X: test_data, Y: test_label, keep_prob: 1.0}))
    outputs = sess.run(cnn.scores, feed_dict = {X:test_data, Y:test_label, keep_prob:1.0})

    test_label = np.argmax(test_label, axis=1)
    outputs = np.argmax(outputs, axis=1)
    print("=== predictions ===")
    print(outputs)
    print("=== labels ===")
    print(test_label)

    diff = 0
    #for seq_t, seq_p in zip(test_label, outputs):
    for t, p in zip(test_label, outputs):
        if p > 1:
            p = 1
        if t != round(p):
            diff += 1

    acc = 1 - float(diff)/len(test_label)
    print("Accuracy : %s"%(acc))

    f = open('./result/result.cnn.tsv', 'w')
    f.write('%.4f\n'%(acc))
    for test_seq, pred_seq in zip(test_label, outputs):
        f.write('%s\t%s\n'%(test_seq, pred_seq))
    f.close()







