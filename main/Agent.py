import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, optimizers, losses

gpus = tf.config.experimental.list_physical_devices(device_type='GPU')

# for gpu in gpus:
#     tf.config.experimental.set_memory_growth(gpu, True)

# 限制使用2G显存
tf.config.experimental.set_virtual_device_configuration(
    gpus[0],
    [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=2048)]
)

class Policy(keras.Model):
    #策略网络，生成动作概念分布
    def __init__(self, learning_rate, gamma):
        super(Policy, self).__init__()
        #记录轨迹
        self.data = []

        self.fc1 = layers.Dense(50,kernel_initializer='he_normal')
        self.fc2 = layers.Dense(30,kernel_initializer='he_normal')
        self.fc3 = layers.Dense(20) #20条流量，动作是对流量进行选择

        # self.conv1 = layers.Conv2D
        self.gamma = gamma
        self.lr = learning_rate
        #网络优化器
        self.optimizer = optimizers.Adam(lr=self.lr)

    def call(self, inputs, training=None):
        #状态输入长度为tt_num*最大路由
        x = tf.nn.relu(self.fc1(inputs))
        x = tf.nn.relu(self.fc2(x))
        x = self.fc3(x)
        # x = tf.nn.softmax(x, axis=1)
        return x

    def put_data(self, item):
        #记录r, log_P(a|s)
        self.data.append(item)


    def train_net(self, tape):
        # 计算梯度并更新策略网络参数。tape为梯度记录器
        R = 0  # 终结状态的初始回报为0
        for r, log_prob in self.data[::-1]:
            R = r + self.gamma*R

            #这个可能需要改
            loss = -log_prob * R

            with tape.stop_recording():
                grads = tape.gradient(loss, self.trainable_variables)

                self.optimizer.apply_gradients(zip(grads, self.trainable_variables))

        self.data = []

