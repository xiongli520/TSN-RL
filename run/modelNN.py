import tensorflow as tf
import tensorflow.contrib.slim as slim

class TTNetwork(object):
    def __init__(self, scope, sess=0):
        with tf.variable_scope(scope):
            self.inputs = tf.placeholder(shape=[None, 9],dtype=tf.float32)
            self.actions = tf.placeholder(shape=[None, 1],dtype=tf.float32)
            self.rewards = tf.placeholder(shape=[None],dtype=tf.float32)

            trainer_location = tf.train.AdamOptimizer(learning_rate=0.0005,name='adam_lo')
            trainer_rl = tf.train.AdamOptimizer(learning_rate=0.0001,name='adam_rl')

            # output
            net = slim.fully_connected(self.inputs, 256, activation_fn=tf.nn.elu)
            net = slim.fully_connected(net, 256, activation_fn=tf.nn.elu)
            net = slim.fully_connected(net, 256, activation_fn=tf.nn.elu)
            net = slim.fully_connected(net, 256, activation_fn=tf.nn.elu)
            self.outt = slim.fully_connected(net, 1, activation_fn=None)
            #self.outt = self.net_location(self.inputs)
            #self.outt = self.outt # * 16.588
            self.out = tf.clip_by_value(self.outt, 0., 16.588) # 16.588 = log(16000000)

            # parameters
            self.local_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope)

            # reinforcement learning loss
            self.tt_loss_rl = tf.reduce_sum(tf.square(self.outt - self.actions) * self.actions)
            self.train_rl = trainer_rl.minimize(self.tt_loss_rl)

            # imitiation learning loss
            self.tt_loss_sl = tf.reduce_mean(tf.square(self.outt - self.actions) * self.actions)
            self.train_sl = trainer_location.minimize(self.tt_loss_sl)

            self.sess = sess
            self.sess.run(tf.global_variables_initializer())