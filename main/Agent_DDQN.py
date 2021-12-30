import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, optimizers, losses
import collections
import numpy as np
import random

gpus = tf.config.experimental.list_physical_devices(device_type='GPU')

# for gpu in gpus:
#     tf.config.experimental.set_memory_growth(gpu, True)

# 限制使用2G显存
tf.config.experimental.set_virtual_device_configuration(
    gpus[0],
    [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=2048)]
)

class ReplayBuffer:
    # 经验回放池
    def __init__(self, buffer_limit):
        # 双向队列
        self.buffer = collections.deque(maxlen=buffer_limit)

    def put(self, transition):
        self.buffer.append(transition)

    def sample(self, n):
        # 从回放池采样n个5元组
        mini_batch = random.sample(self.buffer, n)
        s_lst, a_lst, r_lst, s_prime_lst, done_mask_lst = [], [], [], [], []
        # 按类别进行整理
        for transition in mini_batch:
            s, a, r, s_prime, done_mask = transition
            s_lst.append(s)
            a_lst.append([a])
            r_lst.append([r])
            s_prime_lst.append(s_prime)
            done_mask_lst.append([done_mask])
        # 转换成Tensor
        return tf.constant(s_lst, dtype=tf.float32), \
               tf.constant(a_lst, dtype=tf.int32), \
               tf.constant(r_lst, dtype=tf.float32), \
               tf.constant(s_prime_lst, dtype=tf.float32), \
               tf.constant(done_mask_lst, dtype=tf.float32)

    def size(self):
        return len(self.buffer)


class Qnet(keras.Model):
    def __init__(self, action_size):
        # 创建Q网络，输入为状态向量，输出为动作的Q值
        super(Qnet, self).__init__()
        self.action_size = action_size
        self.fc1 = layers.Dense(100, kernel_initializer='he_normal')
        self.fc2 = layers.Dense(50, kernel_initializer='he_normal')
        self.fc3 = layers.Dense(action_size, kernel_initializer='he_normal')

    def call(self, x, training=None):
        x = tf.nn.relu(self.fc1(x))
        x = tf.nn.relu(self.fc2(x))
        x = self.fc3(x)
        return x

    def sample_action(self, s, epsilon):
        # 送入状态向量，获取策略: [4]
        s = tf.constant(s, dtype=tf.float32)
        # s: [4] => [1,4]
        s = tf.expand_dims(s, axis=0)
        out = self(s)[0]
        coin = random.random()
        # 策略改进：e-贪心方式
        if coin < epsilon:
            # epsilon大的概率随机选取
            return random.randint(0, self.action_size-1)
        else:  # 选择Q值最大的动作
            return int(tf.argmax(out))

def train(q, q_target, memory, optimizer, batch_size, gamma):
    for i in range(10):
        # 从缓冲池采样
        s, a, r, s_prime, done_mask = memory.sample(batch_size)
        with tf.GradientTape() as tape:
            # s: [b, 60]
            q_out = q(s)  # 得到Q(s,a)的分布
            # 由于TF的gather_nd与pytorch的gather功能不一样，需要构造
            # gather_nd需要的坐标参数，indices:[b, 2]
            # pi_a = pi.gather(1, a) # pytorch只需要一行即可实现
            indices = tf.expand_dims(tf.range(a.shape[0]), axis=1)
            indices = tf.concat([indices, a], axis=1)
            q_a = tf.gather_nd(q_out, indices)  # 动作的概率值, [b]
            q_a = tf.expand_dims(q_a, axis=1)  # [b]=> [b,1]
            # 得到Q(s',a)的最大值，它来自影子网络！ [b,4]=>[b,2]=>[b,1]
            a_ = tf.expand_dims(tf.argmax(q(s_prime), axis=1), axis=1)
            a_ = tf.cast(a_, tf.int32)
            indices_ = tf.expand_dims(tf.range(a.shape[0]), axis=1)
            indices_ = tf.concat([indices_, a_], axis=1)
            max_q_prime = tf.gather_nd(q_target(s_prime), indices_)
            # max_q_prime = tf.reduce_max(q_target(s_prime), axis=1, keepdims=True)
            # 构造Q(s,a_t)的目标值，来自贝尔曼方程
            target = r + gamma * max_q_prime
            # 计算Q(s,a_t)与目标值的误差
            loss = losses.MSE(target, q_a)
            # 更新网络，使得Q(s,a_t)估计符合贝尔曼方程
            grads = tape.gradient(loss, q.trainable_variables)
            optimizer.apply_gradients(zip(grads, q.trainable_variables))