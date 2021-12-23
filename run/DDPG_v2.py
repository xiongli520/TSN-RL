import tensorflow as tf
import numpy as np
import tensorflow.contrib.slim as slim
import env_tt.util as util

np.random.seed(1)
tf.set_random_seed(1)

# all placeholder for tf
with tf.name_scope('S'):
    S = tf.placeholder(tf.float32, shape=[None, 995], name='s')
with tf.name_scope('R'):
    R = tf.placeholder(tf.float32, [None, 1], name='r')
with tf.name_scope('S_'):
    S_ = tf.placeholder(tf.float32, shape=[None, 995], name='s_')

###################### Actor #########################

class Actor():
    def __init__(self, sess, action_dim, action_bound, state_dim, learning_rate, replacement):
        self.sess = sess
        self.a_dim = action_dim
        self.action_bound = action_bound
        self.state_dim = state_dim
        self.lr = learning_rate
        self.replacement = replacement
        self.t_replace_counter = 0


        with tf.variable_scope('Actor'):
            #input s, output a
            self.a = self._build_net(S, scope='eval_net', trainable=True)
            #self.a = a * 13.81
            #input s_ ouput a, get a_ for critic
            self.a_ = self._build_net(S_, scope='target_net', trainable=False)

        self.e_params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES,scope='Actor/eval_net')
        self.t_params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES,scope='Actor/target_net')

        #parameter replacement
        self.t_replace_counter = 0
        self.replacement_run = [tf.assign(t, e) for t, e in zip(self.t_params, self.e_params)]

    def _build_net(self, s, scope, trainable):
        with tf.variable_scope(scope):
            # output
            net = slim.fully_connected(s, 800, activation_fn=tf.nn.elu, trainable=trainable)
            net = slim.fully_connected(net, 400, activation_fn=tf.nn.elu, trainable=trainable)
            net = slim.fully_connected(net, 200, activation_fn=tf.nn.elu, trainable=trainable)
            net = slim.fully_connected(net, 100, activation_fn=tf.nn.elu, trainable=trainable)
            outt = slim.fully_connected(net, 1, activation_fn=None, trainable=trainable)

            out = tf.clip_by_value(outt, 0., 13.815)  # 13.815 = log(1000000)
        return out

    def choose_action(self, s):
        s = s[np.newaxis, :]    # single state
        return self.sess.run(self.a, feed_dict={S: s})[0]   #single action

    # def choose_final_action(self, s):
    #     s = s[np.newaxis, :]    # single state
    #     a = self.sess.run(self.a, feed_dict={self.S: s})[0]


    def add_grad_to_graph(self, a_grads):
        with tf.variable_scope('policy_grads'):
            # ys = policy;
            # xs = policy's parameters;
            # a_grads = the gradients of the policy to get more Q
            # tf.gradients will calculate dys/dxs with a initial gradients for ys, so this is dq/da * da/dparams
            self.policy_grads = tf.gradients(ys=self.a, xs=self.e_params, grad_ys=a_grads)

        with tf.variable_scope('A_train'):
            opt = tf.train.AdamOptimizer(-self.lr)  # (- learning rate) for ascent policy
            self.train_op = opt.apply_gradients(zip(self.policy_grads, self.e_params))

    def learn(self, s):
        self.sess.run(self.train_op, feed_dict={S: s})

        if self.t_replace_counter % self.replacement == 0:
            self.sess.run(self.replacement_run)


#################### Critic #####################
class Critic():
    def __init__(self, sess, state_dim, action_dim, learning_rate, gamma, replacement, a, a_):
        self.sess = sess
        self.state_dim = state_dim
        self.a_dim = action_dim
        self.lr = learning_rate
        self.gamma = gamma
        self.replacement = replacement


        with tf.variable_scope('Critic'):
            # Input (s, a), output q
            self.a = tf.stop_gradient(a)    # stop critic update flows to actor
            self.q = self._build_net(S, self.a, 'eval_net', trainable=True)

            # Input (s_, a_), output q_ for q_target
            self.q_ = self._build_net(S_, a_, 'target_net', trainable=False)    # target_q is based on a_ from Actor's target_net

            self.e_params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope='Critic/eval_net')
            self.t_params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope='Critic/target_net')

            with tf.variable_scope('target_q'):
                self.target_q = R + self.gamma * self.q_

            with tf.variable_scope('TD_error'):
                self.loss = tf.reduce_mean(tf.squared_difference(self.target_q, self.q))

            with tf.variable_scope('C_train'):
                self.train_op = tf.train.AdamOptimizer(self.lr).minimize(self.loss)

            with tf.variable_scope('a_grad'):
                self.a_grads = tf.gradients(self.q, self.a)[0]  # tensor of gradients of each sample (None, a_dim)

            self.t_replace_counter = 0
            self.replacement_run = [tf.assign(t, e) for t, e in zip(self.t_params, self.e_params)]

    def _build_net(self, s, a, scope, trainable):
        with tf.variable_scope(scope):
            # output
            init_w = tf.random_normal_initializer(0., 0.1)
            init_b = tf.constant_initializer(0.1)
            with tf.variable_scope('l1'):
                n_l1 = 100
                w1_s = tf.get_variable('w1_s', [self.state_dim, n_l1], initializer=init_w, trainable=trainable)
                w1_a = tf.get_variable('w1_a', [self.a_dim, n_l1], initializer=init_w, trainable=trainable)
                b1 = tf.get_variable('b1', [1, n_l1], initializer=init_b, trainable=trainable)
                net = tf.nn.relu(tf.matmul(s, w1_s) + tf.matmul(a, w1_a) + b1)

            net = slim.fully_connected(net, 256, activation_fn=tf.nn.elu, trainable=trainable)
            net = slim.fully_connected(net, 256, activation_fn=tf.nn.elu, trainable=trainable)
            net = slim.fully_connected(net, 256, activation_fn=tf.nn.elu, trainable=trainable)
            q = slim.fully_connected(net, 1, activation_fn=None, trainable=trainable)
        return q

    def learn(self, s, a, r, s_):
        self.sess.run(self.train_op, feed_dict={S: s, self.a: a, R: r, S_: s_})
        if self.t_replace_counter % self.replacement == 0:
            self.sess.run(self.replacement_run)

    # def check(self, s, aa, r, s_):
    #     q_ = self.sess.run(self.q, feed_dict={S:s, self.a: aa})
    #     return q_, self.a


############## Memory ####################

class Memory():
    def __init__(self,capacity,dims):
        self.capacity = capacity
        self.data = np.zeros((capacity,dims))
        self.pointer = 0

    def store_transition(self, s, a, r, s_):
        transition = np.hstack((s, a, r, s_))
        index = self.pointer % self.capacity        # replace the old memory with new memory
        self.data[index, :] = transition
        self.pointer += 1

    def sample(self, n):
        assert self.pointer >= self.capacity, 'Memory has not been fulfilled'
        indices = np.random.choice(self.capacity, size=n)
        return self.data[indices, :]
