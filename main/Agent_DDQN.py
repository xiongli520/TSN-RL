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