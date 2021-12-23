import env_tt.util as util
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
        num_frames = len(self.tt_frames)
        state = util.state_generation(tt_frame=self.tt_frames[0], paths=self.paths, rest_frame_num=num_frames,
                                      min_lcm=16000000)
        self.rest_frame_num = num_frames - 1
        return state

    def update_paths(self, start, stop, tt_frame):
        '''
        通过得到的start和stop和帧信息来更新当前paths信息
        :param start: 帧发送时刻列表
        :param stop: 帧结束发送时刻列表
        :param tt_frame: 帧信息
        :return: 更新paths
        '''
        if start != -1:
            path_through = tt_frame[2]  # 表示该帧通过的物理链路列表
            quantity = self.min_lcm // tt_frame[1]
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
        tt_frame = util.get_frame(self.tt_frames, self.rest_frame_num)
        start, stop = util.get_start_stop(a, tt_frame, self.paths)
        is_match_condition = util.match_condition(start, stop, tt_frame, self.paths, min_lcm=16000000)
        if is_match_condition:
            self.update_paths(start, stop, tt_frame)
            self.rest_frame_num -= 1
            next_state = util.state_generation(tt_frame, self.paths, self.rest_frame_num, self.min_lcm)
            self.reward = 1
            self.done = util.isdone(self.rest_frame_num)
            return next_state, self.reward, self.done, math.log(start[0])
        else:
            next_state = util.state_generation(tt_frame, self.paths, self.rest_frame_num, self.min_lcm)
            print('get crash')
            self.reward = -10
            self.done = True
            return next_state, self.reward, True, math.log(a)

