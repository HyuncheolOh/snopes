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


trainset = ToySequenceData(X_train, y_train, max_length)
testset = ToySequenceData(X_test, y_test, max_length)

# Training Parameters
learning_rate = 0.01
num_steps = 300
batch_size = 32
display_step = 10

# Network Parameters
num_input = 784 # MNIST data input (img shape: 28*28)
num_classes = 2 # MNIST total classes (0-9 digits)
dropout = 0.50 # Dropout, probability to keep units

# tf Graph input
#X = tf.placeholder(tf.float32, [None, num_input])
X = tf.placeholder(tf.float32, [None, max_length,  100])
Y = tf.placeholder(tf.float32, [None, num_classes])
keep_prob = tf.placeholder(tf.float32) # dropout (keep probability)


# Create some wrappers for simplicity
def conv2d(x, W, b, strides=1):
    # Conv2D wrapper, with bias and relu activation
    x = tf.nn.conv2d(x, W, strides=[1, strides, strides, 1], padding='SAME')
    x = tf.nn.bias_add(x, b)
    return tf.nn.relu(x)


def maxpool2d(x, k=2):
    # MaxPool2D wrapper
    return tf.nn.max_pool(x, ksize=[1, k, k, 1], strides=[1, k, k, 1],
                          padding='SAME')


# Create model
def conv_net(x, weights, biases, dropout):
    # MNIST data input is a 1-D vector of 784 features (28*28 pixels)
    # Reshape to match picture format [Height x Width x Channel]
    # Tensor input become 4-D: [Batch Size, Height, Width, Channel]
    #x = tf.reshape(x, shape=[-1, 28, 28, 1])
    x = tf.reshape(x, shape=[-1, max_length, 100, 1])

    # Convolution Layer
    conv1 = conv2d(x, weights['wc1'], biases['bc1'])
    # Max Pooling (down-sampling)
    conv1 = maxpool2d(conv1, k=2)
    print(conv1.get_shape())
    # Convolution Layer
    conv2 = conv2d(conv1, weights['wc2'], biases['bc2'])
    # Max Pooling (down-sampling)
    conv2 = maxpool2d(conv2, k=2)
    print(conv2.get_shape())
    # Fully connected layer
    # Reshape conv2 output to fit fully connected layer input
    fc1 = tf.reshape(conv2, [-1, weights['wd1'].get_shape().as_list()[0]])
    fc1 = tf.add(tf.matmul(fc1, weights['wd1']), biases['bd1'])
    fc1 = tf.nn.relu(fc1)
    # Apply Dropout
    fc1 = tf.nn.dropout(fc1, dropout)

    # Output, class prediction
    out = tf.add(tf.matmul(fc1, weights['out']), biases['out'])
    return out

# Store layers weight & bias
weights = {
    # 5x5 conv, 1 input, 32 outputs
    'wc1': tf.Variable(tf.random_normal([5, 5, 1, 32])),
    # 5x5 conv, 32 inputs, 64 outputs
    'wc2': tf.Variable(tf.random_normal([5, 5, 32, 64])),
    # fully connected, 7*7*64 inputs, 1024 outputs
    #'wd1': tf.Variable(tf.random_normal([7*7*64, 1024])),
    #'wd1': tf.Variable(tf.random_normal([11*25*64, 1024])),
    'wd1': tf.Variable(tf.random_normal([13*25*64, 1024])),
    # 1024 inputs, 10 outputs (class prediction)
    'out': tf.Variable(tf.random_normal([1024, num_classes]))
}

biases = {
    'bc1': tf.Variable(tf.random_normal([32])),
    'bc2': tf.Variable(tf.random_normal([64])),
    'bd1': tf.Variable(tf.random_normal([1024])),
    'out': tf.Variable(tf.random_normal([num_classes]))
}

# Construct model
logits = conv_net(X, weights, biases, keep_prob)
prediction = tf.nn.softmax(logits)

# Define loss and optimizer
loss_op = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(
    logits=logits, labels=Y))
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
train_op = optimizer.minimize(loss_op)


# Evaluate model
correct_pred = tf.equal(tf.argmax(prediction, 1), tf.argmax(Y, 1))
accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

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
            loss, acc, pred = sess.run([loss_op, accuracy, logits], feed_dict={X: batch_x,
                                                                 Y: batch_y,
                                                                 keep_prob: 1.0})
            print("Step " + str(step) + ", Minibatch Loss= " + \
                  "{:.4f}".format(loss) + ", Training Accuracy= " + \
                  "{:.3f}".format(acc))
            print(batch_y)
            print(pred)

    print("Optimization Finished!")

    test_data = testset.data
    test_label = testset.labels
    # Calculate accuracy for 256 MNIST test images
#    print("Testing Accuracy:", sess.run(accuracy, feed_dict={X: test_data, Y: test_label, keep_prob: 1.0}))
    outputs = sess.run(prediction, feed_dict = {X:test_data, Y:test_label, keep_prob:1.0})

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







