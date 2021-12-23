from Data.SimpleNetwork import *
import tensorflow as tf
import numpy as np
from main.util import *

class Env:
    def __init__(self,network):
        self.network = network
        self.cur_flow_id = -1
        self.next_flow_id = -1
        self.cur_flow = {}
        self.next_flow = {}
        self.tt_flows = self.network.tt_flow
        self.max_hop = self.network.max_hop
        self.pre_util = 0
        #时隙状态，代表流调度时，目前的最大截止时间
        self.slot_state = np.full(shape=self.network.tt_num, fill_value=-1.0)
        #tt流的调度状态矩阵
        self.tt_schedule_matrix = np.zeros(shape=[self.network.tt_num, self.max_hop])
        #tt流路由信息矩阵
        self.tt_route_matrix = np.zeros(shape=[self.network.tt_num, self.max_hop])
        #tt流周期信息矩阵
        self.tt_period_matrix = np.zeros(shape=[self.network.tt_num, self.max_hop])
        #tt流总的处理时间
        self.all_length = 0


    def reset(self):
        '''
        初始化所有状态
        :return: 
        '''
        # 初始化所以的链路状态
        for edge in self.network.edges.values():
            edge.edge_reset()
        self.slot_state = np.full(shape=self.network.tt_num, fill_value=-1.0)

        #初始化tt流的调度状态矩阵
        for i in range(self.network.tt_num):
            hop = len(self.network.tt_flow[str(i)]['edge_path'])
            flow_rout = self.network.tt_flow[str(i)]['edge_path']
            flow_period = self.network.tt_flow[str(i)]['cycle']
            for j in range(hop):
                self.tt_schedule_matrix[i][j] = self.network.tt_flow[str(i)]['pkt_len']
                self.tt_route_matrix[i][j] = flow_rout[j]
                self.tt_period_matrix[i][j] = flow_period

        # tt流总的处理时间
        self.all_length = np.sum(self.tt_schedule_matrix)

        state = self.output_state()
        print('reset success!!!')
        return state

    def get_next_flow(self, next_flow_id):
        '''
        通过获取下一个流的id编号得到下一条流的信息
        :param next_flow_id: 
        :return: 
        '''
        self.next_flow = self.tt_flows[next_flow_id]
        self.cur_flow = self.next_flow
        self.next_flow = {}

    def get_flow_normal(self):
        '''
        通过按顺序的方式得到下一条要调度的流
        :return: 
        '''
        if self.tt_flows and self.cur_flow_id != -1:
            self.next_flow_id = self.cur_flow_id + 1
            return self.next_flow_id
        else:
            print("get flow normal ERROR!!!")
            return -1

    def output_state(self):
        '''
        将状态转换为输入神经网络的
        :return: 
        '''
        if np.any(self.tt_schedule_matrix): #当tt_schedule_matrix不全为0时
            return self.tt_schedule_matrix.flatten()
        else:
            print('全为0')
            return np.full(shape=60, fill_value=0)

    def constrain(self):
        '''
        判断各个流量是否调度完成
        :param action: 
        :return: 
        '''
        is_zeros = []
        for tt_index in range(self.network.tt_num):
            tt_flow = self.tt_schedule_matrix[tt_index][:]
            is_zeros.append(np.any(tt_flow))
        if is_zeros:
            return is_zeros
        else:
            return [False]

    def step(self, a):
        '''
        输入动作，得到之后的状态，奖励等
        :param a: 
        :return: 
        '''
        # 判断是否是一个有效的动作
        # 确定使用链路序号
        index, edge_index, period, flow_length = self.get_link(a)
        result = self.network.occupy_edge_slot(edge_index=edge_index, flow_length=flow_length, action=a,
                                      flow_end_slot=self.slot_state[a])
        self.slot_state[a] = self.network.edges[edge_index].current_slot

        if result == 'success':
            # r = self.get_reward_fast()
            r = self.get_reward_fast2()
            self.tt_schedule_matrix[a][index] = 0
            new_state = self.output_state()
            done = self.is_done()
            return new_state, r, done

        elif result == 'fail':
            new_state = self.output_state()
            r = -1
            done = False
            return new_state, r, done

        # if flow_length == 0:
        #     new_state = self.output_state()
        #     r = -1
        #     done = False
        #     return new_state, r, done
        #
        # else:
        #     self.network.occupy_edge_slot(edge_index=edge_index, flow_length=flow_length, action=a, flow_end_slot=self.slot_state[a])
        #     self.slot_state[a] = self.network.edges[edge_index].current_slot
        #     r = self.get_reward_fast()
        #
        #     # state = self.output_state()
        #     self.tt_schedule_matrix[a][index] = 0
        #     new_state = self.output_state()
        #
        #     done = self.is_done()
        #     # print('r:{}'.format(r))
        #     # print('a')
        #     return new_state, r, done

    def get_reward_fast(self):
        '''
        通过执行动作a后，得到的状态，从而得到单步奖励
        :return: 
        '''
        c_max_cur, process_length = self.get_Cmax_Process()
        cur_util = process_length/(self.network.edge_num * c_max_cur)
        r = cur_util - self.pre_util
        self.pre_util = cur_util
        return r

    def get_reward_fast2(self):
        '''
        通过执行动作a后，得到的状态，从而得到单步奖励
        与fast方法不同是，不考虑已调度的消息这个因素，只看分母的目前的最大make span
        分子为所有流的总共的处理时间
        :return: 
        '''
        c_max_cur, process_length = self.get_Cmax_Process()
        cur_util = self.all_length/(self.network.edge_num * c_max_cur)
        r = cur_util - self.pre_util
        self.pre_util = cur_util
        return r


    def get_Cmax_Process(self):
        '''
        得到当前链路中最大的使用时间和已经处理的tt流的总长度
        :return: 
        '''
        C_max = 0
        Process_length = 0
        for edge in self.network.edges.values():
            Process_length += edge.occupy_length
            if C_max < edge.current_slot:
                C_max = edge.current_slot
        return C_max+1, Process_length
        
    def get_link(self, a):
        '''
        得到调度的链路序号
        :param a: 
        :return: 
        '''
        index = 0
        flow_list = self.tt_schedule_matrix[a, :]
        route_list = self.tt_route_matrix[a, :]
        period_list = self.tt_period_matrix[a, :]
        for i in range(len(flow_list)):
            if flow_list[i] != 0:
                index = i
                break
        flow_length = flow_list[index]
        edge_index = route_list[index]
        period = period_list[index]

        return index, edge_index, period, flow_length

    def is_done(self):
        '''
        判断是否调度完成
        :return: 
        '''
        if np.any(self.tt_schedule_matrix): #当tt_schedule_matrix不全为0时
            return False
        else:
            print('调度完成!')
            return True

    def preprocess(self, is_zeros, min_tf):
        '''
        如果某一不满足约束，调度完成了，就将其选择概念置为0
        :param is_zeros: 
        :return: 
        '''
        np_w = np.identity(self.network.tt_num)
        np_b = np.zeros(self.network.tt_num)
        for i in range(len(is_zeros)):
            if not is_zeros[i]:
                np_w[i][i] = 0.0
                np_b[i] = min_tf
        return np_w, np_b


if __name__ == '__main__':
    simplenetwork = SimpleNetwork()
    simplenetwork.generateAll(fileName='SimpleNetwork',node_num=10, end_num=8, switch_num=2, rand_min=10,
                     rand_max=30, tt_num=20, delay_min=10, delay_max=20,
                     pkt_min=32, pkt_max=64, dynamic=False)
    # simplenetwork.writeToFile(fileName='SimpleNetwork')
    env = Env(simplenetwork)
    env.reset()
    env.step(2)
    env.step(2)
    env.step(2)
    is_zeros = env.constrain()
    # np_unit = env.preprocess(is_zeros)
    # print(is_zeros)
    # print(np_unit)
