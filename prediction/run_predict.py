""" Dynamic Recurrent Neural Network.
TensorFlow implementation of a Recurrent Neural Network (LSTM) that performs
dynamic computation over sequences with variable length. This example is using
a toy dataset to classify linear sequences. The generated sequences have
variable length.
Links:
    [Long Short Term Memory](http://deeplearning.cs.cmu.edu/pdfs/Hochreiter97_lstm.pdf)
Author: Aymeric Damien
Project: https://github.com/aymericdamien/TensorFlow-Examples/
"""

from __future__ import print_function
import os
import tensorflow as tf
import time
import random
import sys
import dataload
import numpy as np
import util_sampling as sampling
import comment_data_load as comment_load
from sklearn.model_selection import train_test_split

# ====================
#  TOY DATA GENERATOR
# ====================
class ToySequenceData(object):
    """ Generate sequence of data with dynamic length.
    This class generate samples for training:
    - Class 0: linear sequences (i.e. [0, 1, 2, 3,...])
    - Class 1: random sequences (i.e. [1, 3, 10, 7,...])
    NOTICE:
    We have to pad each sequence to reach 'max_seq_len' for TensorFlow
    consistency (we cannot feed a numpy array with inconsistent
    dimensions). The dynamic calculation will then be perform thanks to
    'seqlen' attribute that records every actual sequence length.
    """

    def __init__(self, X, y, max_length):
        self.data = []
        self.labels = [] #one hot [1.0, 0.0]
        self.seqlen = []
        '''
        for i in range(n_samples):
            # Random sequence length
            len = random.randint(min_seq_len, max_seq_len)
            # Monitor sequence length for TensorFlow dynamic calculation
            self.seqlen.append(len)
            # Add a random or linear int sequence (50% prob)
            if random.random() < .5:
                # Generate a linear sequence
                rand_start = random.randint(0, max_value - len)
                s = [[float(i) / max_value] for i in
                     range(rand_start, rand_start + len)]
                # Pad sequence for dimension consistency
                s += [[0.] for i in range(max_seq_len - len)]
                self.data.append(s)
                self.labels.append([1., 0.])
            else:
                # Generate a random sequence
                s = [[float(random.randint(0, max_value)) / max_value]
                     for i in range(len)]
                # Pad sequence for dimension consistency
                s += [[0.] for i in range(max_seq_len - len)]
                self.data.append(s)
                self.labels.append([0., 1.])
        '''
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
# =========
# arg
# ========

# ==========
#   MODEL
# ==========
model_name = sys.argv[1]
model_path = os.path.abspath(os.path.join(os.path.curdir, "model/%s/%s.ckpt"%(model_name, model_name)))
print(model_path)

# Parameters
learning_rate = 0.01
epoch = 1
batch_size = 100 
display_step = 100

# Network Parameters
n_hidden = 100  # hidden layer num of features
n_classes = 2  # linear sequence or not

#X, y = dataload.get_claim_veracity()
#X, y = dataload.get_claim_veracity_2018()
#X, y = dataload.get_snopes_data()

year = sys.argv[2]
X, y = dataload.get_snopes_politics(year)
#X, y = dataload.get_politifact_data(year)

print("After sampling. Test data - non-zero : %s, total : %s"%(np.count_nonzero(y), len(y)))
max_length = len(max(X, key=len))
seq_max_len = max_length # Sequence max length
print(seq_max_len)

testset = ToySequenceData(X, y, seq_max_len)

#print(trainset.seqlen)

# tf Graph input
x = tf.placeholder("float", [None, seq_max_len, 100])
y = tf.placeholder("float", [None, n_classes])
# A placeholder for indicating each sequence length
seqlen = tf.placeholder(tf.int32, [None])

# Define weights
weights = {
    'out': tf.Variable(tf.random_normal([n_hidden, n_classes]))
}
biases = {
    'out': tf.Variable(tf.random_normal([n_classes]))
}


def dynamicRNN(x, seqlen, weights, biases):
    # Prepare data shape to match `rnn` function requirements
    # Current data input shape: (batch_size, n_steps, n_input)
    # Required shape: 'n_steps' tensors list of shape (batch_size, n_input)

    # Unstack to get a list of 'n_steps' tensors of shape (batch_size, n_input)
    x = tf.unstack(x, seq_max_len, 1)

    # Define a lstm cell with tensorflow
    lstm_cell = tf.contrib.rnn.BasicLSTMCell(n_hidden)
    lstm_cell = tf.contrib.rnn.DropoutWrapper(lstm_cell, output_keep_prob=0.5)
    # Get lstm cell output, providing 'sequence_length' will perform dynamic
    # calculation.
    outputs, states = tf.contrib.rnn.static_rnn(lstm_cell, x, dtype=tf.float32,
                                                sequence_length=seqlen)

    # When performing dynamic calculation, we must retrieve the last
    # dynamically computed output, i.e., if a sequence length is 10, we need
    # to retrieve the 10th output.
    # However TensorFlow doesn't support advanced indexing yet, so we build
    # a custom op that for each sample in batch size, get its length and
    # get the corresponding relevant output.

    # 'outputs' is a list of output at every timestep, we pack them in a Tensor
    # and change back dimension to [batch_size, n_step, n_input]
    outputs = tf.stack(outputs)
    outputs = tf.transpose(outputs, [1, 0, 2])

    # Hack to build the indexing and retrieve the right output.
    batch_size = tf.shape(outputs)[0]
    # Start indices for each sample
    index = tf.range(0, batch_size) * seq_max_len + (seqlen - 1)
    # Indexing
    outputs = tf.gather(tf.reshape(outputs, [-1, n_hidden]), index)

    # Linear activation, using outputs computed above
    return tf.matmul(outputs, weights['out']) + biases['out']


pred = dynamicRNN(x, seqlen, weights, biases)

# Define loss and optimizer
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred, labels=y))
#optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate).minimize(cost)
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

# Evaluate model
correct_pred = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

# Initialize the variables (i.e. assign their default value)
init = tf.global_variables_initializer()
saver = tf.train.Saver()
# Start training
with tf.Session() as sess:
    # Run the initializer
    sess.run(init)
    """
    repeat = len(X_train) / batch_size + 1
    for step in range(0, repeat * epoch + 1):
        batch_x, batch_y, batch_seqlen = trainset.next(batch_size)
        # Run optimization op (backprop)
        sess.run(optimizer, feed_dict={x: batch_x, y: batch_y,
                                       seqlen: batch_seqlen})
        if step % display_step == 0 or step == 1:
            
            # Calculate batch accuracy & loss
            p, acc, loss = sess.run([pred, accuracy, cost], feed_dict={x: batch_x, y: batch_y,
                                                              seqlen: batch_seqlen})
            
            print("Step " + str(step) + ", Minibatch Loss= " + \
                  "{:.6f}".format(loss) + ", Training Accuracy= " + \
                  "{:.5f}".format(acc))
    print("Optimization Finished!")
    """
    saver.restore(sess, model_path)

    # Calculate accuracy
    test_data = testset.data
    test_label = testset.labels
    test_seqlen = testset.seqlen
    
    #acc = sess.run(accuracy, feed_dict={x: test_data, y: test_label, seqlen: test_seqlen})
    #print("Testing Accuracy:", sess.run(accuracy, feed_dict={x: test_data, y: test_label, seqlen: test_seqlen}))
    outputs = sess.run(pred, feed_dict={x: test_data, y: test_label, seqlen: test_seqlen})
    outputs = np.argmax(outputs, axis=1)
    test_label = np.argmax(test_label, axis=1)
    print("===predict===")
    print(outputs)
    print("===labels===")
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

    f = open('./result/result.lstm.tsv', 'w')
    f.write('%.4f\n'%(acc))
    for test_seq, pred_seq in zip(test_label, outputs):
        f.write('%s\t%s\n'%(test_seq, pred_seq))
    f.close()


