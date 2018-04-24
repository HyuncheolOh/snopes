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


#data load 
_X, _y = dataload.get_claim_veracity()
#_X, _y = dataload.get_politifact_data()
max_length = len(max(_X, key=len))

X_train, X_test, y_train, y_test = train_test_split(_X, _y, test_size = 0.20, random_state = 42)
X_train, y_train = sampling.sampling('SMOTE', X_train, y_train)
X_train, _, y_train, _ = train_test_split(X_train, y_train, test_size=0.0, random_state=42)

print("After sampling. Train data - non-zero : %s, total : %s"%(np.count_nonzero(y_train), len(y_train)))
print("After sampling. Test data - non-zero : %s, total : %s"%(np.count_nonzero(y_test), len(y_test)))
flags.DEFINE_string("filter_sizes", "3,4,5", "Comma-separated filter sizes (default: '3,4,5')")
flags.DEFINE_integer("num_filters", 128, "Number of filters per filter size (default: 128)")
FLAGS = tf.flags.FLAGS
FLAGS._parse_flags()
trainset = ToySequenceData(X_train, y_train, max_length)
testset = ToySequenceData(X_test, y_test, max_length)
# Training Parameters
learning_rate = 0.01
num_steps = 10000
batch_size = 12
display_step = 50
embedding_size = 100
# Network Parameters
num_input = 784 # MNIST data input (img shape: 28*28)
num_classes = 2 # MNIST total classes (0-9 digits)
dropout = 0.75 # Dropout, probability to keep units
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
optimizer = tf.train.AdamOptimizer(1e-3)
grads_and_vars = optimizer.compute_gradients(cnn.loss)
train_op = optimizer.apply_gradients(grads_and_vars, global_step=global_step)


# Evaluate model
#correct_pred = tf.equal(tf.argmax(cnn.prediction, 1), tf.argmax(Y, 1))
#accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

# Initialize the variables (i.e. assign their default value)
init = tf.global_variables_initializer()

# Start training
with tf.Session() as sess:

    # Run the initializer
    sess.run(init)

    for step in range(1, num_steps+1):
        batch_x, batch_y, _ = trainset.next(batch_size)
        # Run optimization op (backprop)
        sess.run(train_op, feed_dict={X: batch_x, Y: batch_y, keep_prob: 0.5})
        if step % display_step == 0 or step == 1:
            # Calculate batch loss and accuracy
            outputs, loss, acc = sess.run([cnn.scores, cnn.loss, cnn.accuracy], feed_dict={X: batch_x,
                                                                 Y: batch_y,
                                                                 keep_prob: 1.0})
            print("Step " + str(step) + ", Minibatch Loss= " + \
                  "{:.4f}".format(loss) + ", Training Accuracy= " + \
                  "{:.3f}".format(acc))
            #print(np.argmax(batch_y, axis=1))
            #print(np.argmax(outputs, axis=1))

    print("Optimization Finished!")

    test_data = testset.data
    test_label = testset.labels
    # Calculate accuracy for 256 MNIST test images
#    print("Testing Accuracy:", sess.run(accuracy, feed_dict={X: test_data, Y: test_label, keep_prob: 1.0}))
    outputs = sess.run(cnn.scores, feed_dict = {X:test_data, Y:test_label, keep_prob:1.0})

    test_label = np.argmax(test_label, axis=1)
    outputs = np.argmax(outputs, axis=1)
    print(test_label)
    print(outputs)

    diff = 0
    #for seq_t, seq_p in zip(test_label, outputs):
    for t, p in zip(test_label, outputs):
        if p > 1:
            p = 1
        if t != round(p):
            diff += 1

    acc = 1 - float(diff)/len(test_label)
    print("Accuracy : %s"%(acc))

    f = open('./result/result.news.tsv', 'w')
    f.write('%.4f\n'%(acc))
    for test_seq, pred_seq in zip(test_label, outputs):
        f.write('%s\t%s\n'%(test_seq, pred_seq))
    f.close()







