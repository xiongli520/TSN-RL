import env_tt.util_4 as util
import numpy as np
import math

class env():
    def __init__(self, action_dim, action_space, observation_dim, tt_frames, paths, min_lcm, C):
        self.action_dim = action_dim
        self.action_space = action_space
        self.observation_dim = observation_dim
        self.tt_frames = tt_frames
        self.paths = paths
        # self.paths = [[], [], [], [], [], [], [], [], [], [],
        #          [], [], [], [], [], [], [], [], [], [],
        #          [], [], [], [], [], [], [], [], [], [],
        #          [], [], [], [], [], [], [], [], [], [],
        #          [], [], [], [], [], [], [], [], [], [],
        #          [], [], [], [], [], [], [], [], [], [], [], []]
        self.min_lcm =min_lcm
        self.C = C
        self.tt_delay = []

    def reset(self):
        '''
        初始化整个调度对象，返回第一个状态s1
        :return: 
        '''
        self.paths = [[], [], [], [], [], [], [], [], [], [],
                      [], [], [], [], [], [], [], [], [], [],
                      [], [], [], [], [], [], [], [], [], [],
                      [], [], [], [], [], [], [], [], [], [],
                      [], [], [], [], [], [], [], [], [], [],
                      [], [], [], [], [], [], [], [], [], [], [], []]
        self.rest_frame_num = len(self.tt_frames)
        # path_state = np.empty(16*62)
        path_state = np.zeros(16*62)
        frame_state = np.zeros(3)
        tt_frame = util.get_frame(self.tt_frames, self.rest_frame_num)
        frame_state[0] = tt_frame[0] / tt_frame[1]
        frame_state[1] = self.min_lcm//tt_frame[1]  #quantity
        frame_state[2] = len(tt_frame[2])   #path through num
        self.s = np.hstack((path_state, frame_state))
        return self.s

    def update_paths(self, start, stop, tt_frame):
        '''
       通过得到的start和stop和帧信息来更新当前paths信息
       :param start: 帧发送时刻列表
       :param stop: 帧结束发送时刻列表
       :param tt_frame: 帧信息
       :return: 更新paths
       '''
        if start != -1:
            path_through = tt_frame[2]              #表示该帧通过的物理链路列表
            quantity = self.min_lcm//tt_frame[1]
            for i in range(len(path_through)):
                for j in range(quantity):
                    start_i = start[i] + j * tt_frame[1]
                    stop_i = stop[i] + j * tt_frame[1]
                    self.paths[path_through[i]].append([start_i, stop_i, tt_frame[0], tt_frame[3]])
        else:
            print('start = -1')

    def step(self, a):
        '''
        通过得到的动作（第一条链路发送的开始时刻），得出下一个状态next_state
        :param a: 第一条链路发送的开始时刻
        :return: 
        '''
        use_random = False
        tt_frame = util.get_frame(self.tt_frames, self.rest_frame_num)
        if use_random:
            start, stop, counter = util.find_match_start(tt_frame, self.paths, min_lcm=16000000, counter=0)
            if start == -1:
                print('cant use random find match start')
                self.done = True
                self.reward = -10           #这只是一个暂时的对奖励的解释
            else:
                next_state = util.state_generation(self.s, start, stop, tt_frame, min_lcm=16000000)
        else:
            start, stop = util.get_start_stop(a, tt_frame)

        is_match_condition = util.match_condition(start, stop, tt_frame, self.paths, min_lcm=16000000)
        self.update_paths(start, stop, tt_frame)
        self.rest_frame_num -= 1
        next_tt_frame = util.get_frame(self.tt_frames, self.rest_frame_num)
        next_state = util.state_generation(self.s, start, stop, tt_frame,next_tt_frame, min_lcm=16000000)
        self.s = next_state

        if is_match_condition:
            self.reward = 1
            self.done = util.isdone(self.rest_frame_num)
        else:
            self.reward = -100
            self.done = True

        return self.s, self.reward, self.done, a

    # def get_reward(self, rest_len_num):
    #     reward = rest_len_num


