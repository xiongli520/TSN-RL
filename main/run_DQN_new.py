from main.Agent_DDQN import *
from main.Env_new import *
from Data.SimpleNetwork_new import *
import matplotlib.pyplot as plt
import os
import json
from Data.util import *

os.environ['CUDA_VISIBLE_DEVICES'] = '/gpu:0'

def run():
    node_num = args.node_num
    tt_num = args.tt_num
    end_num = args.end_num
    switch_num = args.switch_num
    util = []
    pkt_len_min = args.pkt_len_min
    pkt_len_max = args.pkt_len_max
    file_name = 'DQN'
    score = 0.0
    print_interval = 20
    # simplenetwork = SimpleNetwork()
    # simplenetwork.generateAll(fileName='SimpleNetwork', node_num=node_num, end_num=end_num, switch_num=switch_num,
    #                           rand_min=10,
    #                           rand_max=30, tt_num=tt_num, delay_min=10, delay_max=20,
    #                           pkt_min=pkt_len_min, pkt_max=pkt_len_max, dynamic=False)


    tt_flows = json.load(open('../Data/resource/unprocess_flow/tt_flows.json'))
    graph = generate_graph('network_info.txt', 'node_info.txt')

    network = SimpleNetwork_new(graph, tt_flows)
    env = Env_new(network)
    q = Qnet(action_size=args.action_size)
    q_target = Qnet(action_size=args.action_size)
    q.build(input_shape=(2,60))
    q_target.build(input_shape=(2,60))
    for src, dest in zip(q.variables, q_target.variables):
        dest.assign(src) # 影子网络权值来自Q
    memory = ReplayBuffer(buffer_limit=args.buffer_limit)  # 创建回放池
    optimizer = optimizers.Adam(lr=args.learning_rate)
    for n_epi in range(1000):  # 训练次数
        # epsilon概率也会30%到1%衰减，越到后面越使用Q值最大的动作
        epsilon = max(0.01, 0.3 - 0.3 * (n_epi / 400))
        s = env.reset()  # 复位环境
        for t in range(60):  # 一个回合最大时间戳
            # if n_epi>1000:
            #     env.render()
            # 根据当前Q网络提取策略，并改进策略
            a = q.sample_action(s, epsilon)
            # 使用改进的策略与环境交互
            s_prime, r, done= env.step(a)
            done_mask = 0.0 if done else 1.0  # 结束标志掩码
            # 保存5元组
            memory.put((s, a, r / 100.0, s_prime, done_mask))
            s = s_prime  # 刷新状态
            # score += r  # 记录总回报
            if done:  # 回合结束
                break
        util.append(env.record[-1])
        if memory.size() > 400: #缓冲池大于400开始训练
            train(q,q_target,memory,optimizer,args.batch_size,args.gamma)

        if n_epi % print_interval == 0 and n_epi != 0:
            # env.network.save_schedule_result(file_name, n_epi)
            for src, dest in zip(q.variables, q_target.variables):
                dest.assign(src)  # 影子网络权值来自Q

    fig, ax = plt.subplots()
    ax.plot(util)
    plt.show()

if __name__ == '__main__':
    run()




