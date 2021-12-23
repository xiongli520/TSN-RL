import math

import numpy as np

import env_tt.util as util


class env():
    def __init__(self,action_dim,action_space,observation_dim,tt_frames,paths,min_lcm,C):
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
        初始化整个调度对象，返回第一个状态
        :return: 
        '''
        self.paths = [[], [], [], [], [], [], [], [], [], [],
                 [], [], [], [], [], [], [], [], [], [],
                 [], [], [], [], [], [], [], [], [], [],
                 [], [], [], [], [], [], [], [], [], [],
                 [], [], [], [], [], [], [], [], [], [],
                 [], [], [], [], [], [], [], [], [], [], [], []]
        num_frames = len(self.tt_frames)
        state = util.state_generation(tt_frame=self.tt_frames[0],paths=self.paths,rest_frame_num=num_frames,min_lcm=16000000)
        self.rest_frame_num = num_frames - 1
        return state

    def update_paths(self,start,stop,tt_frame):
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
                    self.paths[path_through[i]].append([start_i,stop_i,tt_frame[0],tt_frame[3]])
        else:
            print('start = -1')


    def step(self,a):
        '''
        通过得到的动作（第一条链路发送的开始时刻），得出下一个状态next_state
        :param a: 第一条链路发送的开始时刻
        :return: 
        '''
        tt_frame = util.get_frame(self.tt_frames,self.rest_frame_num)
        start, stop, counter = util.get_match_start(a, tt_frame, self.paths)
        if start != -1:
            self.tt_delay.append(util.get_tt_delay(start,stop))
            self.update_paths(start,stop,tt_frame)
            next_state = util.state_generation(tt_frame,self.paths,self.rest_frame_num,self.min_lcm)
            # self.rc_delay = rc_delay.net_calculus(RC_frames.rc_vl,self.C,self.paths)
            self.rest_frame_num -= 1
            self.done = util.isdone(self.rest_frame_num)
            self.reward = self.get_reward2(counter)
            # self.reward = self.get_reward()
            return next_state, self.reward, self.done, math.log(start[0])
        else:
            print('error in step')
            return [-1, -1, -1, -1, -1, -1, -1, -1, -1], -1, True, -1


    def get_reward(self):
        '''
        通过得到的rc延迟和tt延迟计算出本次运算的奖励
        :return: reward = reward_1 * c + reward_2 * (1-c)
        '''
        c = 0.1
        tt_delay_sum = np.sum(self.tt_delay)
        rc_delay_mean = np.mean(self.rc_delay)
        reward_1 = 1 - (tt_delay_sum/1000000.)
        reward_2 = 1 - (rc_delay_mean/300000.)
        reward = reward_1 * c + reward_2 *(1-c)
        return reward

    def get_reward2(self, counter):
        '''
        通过步数和是否能够随机找到合适的start，stop还评定好坏得到奖励
        :return: 
        '''
        if counter == -1:
            return -500
        else:
            return -counter


