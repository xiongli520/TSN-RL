import numpy as np
from main.param import *


class Edge:
    def __init__(self, index, start_node, end_node):
        self.id = index
        self.start_node = start_node
        self.end_node = end_node
        self.time_slot_state = []
        self.global_cycle = args.global_cycle
        #初始化时隙状态，时隙0表示空闲
        self.time_slot_available = np.zeros([self.global_cycle])
        self.current_slot = -1   #表示当前被占领的最后的一个时隙

        self.occupy_length = 0
        self.count = 0
        # for cycle in args.tt_flow_cycles:
        #     self.time_slot_state[cycle] = {i for i in range(cycle)}

    def edge_reset(self):
        '''
        重置链路状态
        :return: 
        '''
        self.time_slot_available = np.zeros([self.global_cycle])
        self.current_slot = -1
        self.occupy_length = 0
        self.count = 0
        self.time_slot_state = []

    def occupy_slot(self, flow_length, start_slot):
        '''
        通过知道流和开始占据的slot开始，将时隙状态改变
        :param flow_length 
        :param start_slot: 
        :return: 
        '''
        if start_slot <= self.global_cycle and flow_length != 0:
            for i in range(flow_length):
                self.time_slot_available[start_slot + i] = 1

        else:
            print('occupy_edge_slot ERROR!!!')


    def occupy_slot_fast(self, action, flow_length, flow_end_slot):
        '''
        通过知道流和开始占据的slot开始，将时隙状态改变
        :param flow_length 
        :param start_slot: 
        :return: 
        '''
        start_slot = max(flow_end_slot, self.current_slot) + 1
        if start_slot + flow_length <= self.global_cycle and flow_length != 0:
            self.time_slot_state.append({})
            self.time_slot_state[-1]['tt_flow'] = action
            self.time_slot_state[-1]['start_slot'] = start_slot
            self.time_slot_state[-1]['end_slot'] = start_slot + flow_length - 1

            for i in range(int(flow_length)):
                self.time_slot_available[int(start_slot + i)] = 1
            self.current_slot = start_slot + flow_length - 1
            self.occupy_length += flow_length
            return 'success'
        else:
            self.count+=1
            print('edge_id{},第{}次 occupy_edge_slot ERROR!!!'.format(self.id, self.count))
            return 'fail'

    def record_occupy_fast(self, flow_length, action, flow_end_slot):
        '''
        记录tt调度表信息,将edge上，被占的时隙，表明是哪一个流量占据
        :param flow_length: 
        :param action: 
        :return: 
        '''
        start_slot = max(flow_end_slot, self.current_slot)
        self.time_slot_state.append({})
        self.time_slot_state[-1]['tt_flow'] = action
        self.time_slot_state[-1]['start_slot'] = start_slot + 1
        self.time_slot_state[-1]['end_slot'] = start_slot + flow_length
