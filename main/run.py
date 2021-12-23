from main.Agent import *
from main.param import *
from main.Env import *
from Data.SimpleNetwork import *
import matplotlib.pyplot as plt

os.environ['CUDA_VISIBLE_DEVICES'] = '/gpu:0'

def run():
    node_num = args.node_num
    tt_num = args.tt_num
    end_num = args.end_num
    switch_num = args.switch_num

    pkt_len_min = args.pkt_len_min
    pkt_len_max = args.pkt_len_max

    lr = args.learning_rate
    gamma = args.gamma

    simplenetwork = SimpleNetwork()
    simplenetwork.generateAll(fileName='SimpleNetwork', node_num=node_num, end_num=end_num, switch_num=switch_num, rand_min=10,
                              rand_max=30, tt_num=tt_num, delay_min=10, delay_max=20,
                              pkt_min=pkt_len_min, pkt_max=pkt_len_max, dynamic=False)

    env = Env(simplenetwork)
    pi = Policy(learning_rate=lr, gamma=gamma)   #创建策略网络
    pi.build(input_shape=(1, 60))
    pi.summary()
    score = 0.0  # 计分
    print_interval = 100  # 打印间隔
    returns = []
    timespan = []
    for n_epi in range(200):
        score = 0.0  # 计分
        s = env.reset() #返回初始状态
        with tf.GradientTape(persistent=True) as tape:
            for i in range(60):
                s = tf.constant(s, dtype=tf.float32)
                s = tf.expand_dims(s, axis=0)
                out = pi(s)
                min_tf = np.array(-99999.99)
                # print('归0前')
                # print(out)
                is_zeros = env.constrain()
                # print(is_zeros)
                np_w, np_b = env.preprocess(is_zeros, min_tf)
                np_w = tf.constant(np_w, dtype=tf.float32)
                np_b = tf.constant(np_b, dtype=tf.float32)
                # print('归0')
                out = tf.matmul(out, np_w) + np_b
                # print(out)
                out = tf.nn.softmax(out, axis=1)
                #
                # new_prob = tf.Variable(prob)
                # for i in range(len(is_zeros)):
                #     if not is_zeros[i]:
                #         new_prob[0,i].assign(tf.reduce_min(prob))
                #
                # prob = tf.convert_to_tensor(new_prob)
                # prob = tf.nn.softmax(prob, axis=1)
                # ssum = tf.reduce_sum(prob)
                # print(ssum)

                # print('softmax后')
                # print(out)
                # 从类别分布中采样1个动作, shape: [1]
                a = tf.random.categorical(tf.math.log(out), 1)[0]
                a = int(a)  # Tensor转数字
                # print('第{}次,选择动作:{}'.format(i, a))
                new_state, r, done = env.step(a)
                # print('r:{}'.format(r))
                # print('a:{}'.format(a))
                pi.put_data((r, tf.math.log(out[0][a])))
                s = new_state
                score = score + r
                if done:
                    print('第{}次  done!!!'.format(n_epi))
                    print('总的分数奖励为:{}'.format(score))
                    print('最大完成时间为:{}'.format(np.max(env.slot_state)))
                    timespan.append(np.max(env.slot_state))
                    break
            pi.train_net(tape=tape)
        del tape
        if n_epi%print_interval == 0:
            env.network.save_schedule_result(n_epi)
        print('===================================================================')

    fig, ax = plt.subplots()
    ax.plot(timespan)
    plt.show()


if __name__ == '__main__':
    run()