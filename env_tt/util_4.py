import frame_process
import numpy as np

from run import RC_frames

np.random.seed(1)

rc_length_sum = RC_frames.path_length_sum
rc_single_sum = RC_frames.path_single_sum
path_each_sum = frame_process.len_frame_eachLk_list
path_each_num = frame_process.num_frame_eachLk_list


def get_start_stop(a, tt_frame, n=0):
    '''
    通过得到的动作a（也就是帧在第一条链路上发送时刻），得到开始发送start和发送结束stop列表
    :param a: 帧在第一条链路上的发送时刻
    :param tt_frame: 帧信息
    :param paths: 当前调度表
    :param n: 参数（用于调节帧的传输延迟）
    :return: start,stop传输链路的发送开始时刻列表和发送结束时刻列表
    '''
    start, stop = [], []
    for i in range(len(tt_frame[2])):  # tt_frame[2]:表示该帧通过的物理链路列表
        if i == 0:
            start_temp = a
            stop_temp = start_temp + tt_frame[0]
            start.append(start_temp)
            stop.append(stop_temp)
        else:
            start_temp = np.random.randint(3000, min(10000, 3001 + 3000 * n / 500)) + stop_temp
            stop_temp = start_temp + tt_frame[0]
            start.append(start_temp)
            stop.append(stop_temp)
    return start, stop

def match_condition(start, stop, tt_frame, paths, min_lcm):
    '''
    通过得到的start和stop列表，和当前的paths调度表对比是否存在窗口重合
    :param start: 帧开始发送时刻
    :param stop: 帧结束发送时刻
    :param tt_frame: 发送的帧信息
    :param paths: 当前调度表
    :param min_lcm: 周期最小公倍数
    :return: True表示满足窗口不重合条件，反之则反
    '''

    if start == -1:
        return False

    path_through = tt_frame[2]      #这个帧会通过的物理链路列表
    quantity = min_lcm//tt_frame[1]
    for h in range(len(path_through)):
        if len(paths[path_through[h]]) == 0:
            continue
        for k in range(quantity):
            y_start = start[h] + k * tt_frame[1]
            y_stop = stop[h] + k * tt_frame[1]
            for l in range(len(paths[path_through[h]])):
                started, stoped = paths[path_through[h]][l][0], paths[path_through[h]][l][1]
                if ((y_start > stoped) or (y_stop < started)) and (y_stop < (k + 1)*tt_frame[1]):
                    pass
                else:
                    return False
    return True

def get_fram_v2(tt_frames,rest_frame_num, rand_1050):
    '''
    通过当前剩余帧数目判断下一个输入的帧
    :return: 
    '''
    index_i = len(tt_frames) - rest_frame_num
    index = rand_1050[index_i]
    return tt_frames[index]

def get_frame(tt_frames,rest_frame_num):
    '''
    通过当前剩余帧数目判断下一个输入的帧
    :return: 
    '''
    index = len(tt_frames) - rest_frame_num
    return tt_frames[index]

def isdone(rest_frames):
    '''
    判断回合是否结束
    :param rest_frames:剩余帧的个数（包括本次需要调度的） 
    :return: done
    '''
    if rest_frames <= 0:
        done = True
    else:
        done = False
    return done

def state_generation(s, start, stop, tt_frame, next_tt_frame, min_lcm):
    '''
    得到下一个状态信息
    :param s:当前状态 
    :param start: 当前帧发送开始时间
    :param stop: 当前帧发送结束时间
    :param tt_frame: 当前帧信息
    :return: next_state
    '''
    path_through = tt_frame[2]          #表示该帧通过的物理链路列表
    quantity = min_lcm//tt_frame[1]
    add_length = round(tt_frame[0]/1000000, 2)
    path_state_matrix = s[:16*62].reshape(62, 16)
    for i in range(len(path_through)):
        for j in range(quantity):
            start_i = start[i] + j * tt_frame[1]
            stop_i = stop[i] + j * tt_frame[1]
            start_index = start_i // 1000000
            stop_index = stop_i // 1000000
            for k in range(int(stop_index - start_index + 1)):
                path_state_matrix[path_through[i]][int(start_index + k)] += add_length
    path_state = path_state_matrix.reshape(16*62)
    frame_state = np.zeros(3)
    frame_state[0] = next_tt_frame[0] / next_tt_frame[1]
    frame_state[1] = min_lcm // next_tt_frame[1]  # quantity
    frame_state[2] = len(next_tt_frame[2])  # path through num
    next_state = np.hstack((path_state, frame_state))
    return next_state

def find_match_start(tt_frame, paths, min_lcm, counter):
    '''
    通过某一种手段，必须找到满足条件的start和stop列表
    :param tt_frame: 帧信息
    :param paths: 当前调度表
    :param min_lcm: 周期最小公倍数
    :return: start,stop传输链路的发送开始时刻列表和发送结束时刻列表
            如果返回为-1，则说明未能找到合适的start和stop
    '''
    start, stop = [], []
    path_through = tt_frame[2]
    counter += 1
    high = np.log(tt_frame[1]-tt_frame[0])
    sample_range = [[0, high/3.], [high/3., (2*high/3.)], [(2*high/3.), high]]

    if counter > 500:
        return -1, -1, -1
    for i in range(len(path_through)):
        if i == 0:
            if counter<25:
                low = sample_range[0][0]
                high = sample_range[0][1]
                start_temp = np.exp(np.random.uniform(low,high))
            elif counter>=25 and counter<75:
                low = sample_range[1][0]
                high = sample_range[1][1]
                start_temp = np.exp(np.random.uniform(low,high))
            elif counter>=75 and counter<500:
                low = sample_range[2][0]
                high = sample_range[2][1]
                start_temp = np.exp(np.random.uniform(low, high))
            else:
                start_temp = np.random.randint(2,tt_frame[1])
            stop_temp = start_temp + tt_frame[0]
        else:
            if counter < 300:
                fx = 10*counter
            else:
                fx = 9*counter - 2400

            start_temp = np.random.randint(3000,min(10000,3001+fx)) + stop_temp
            stop_temp = start_temp + tt_frame[0]

        start.append(start_temp)
        stop.append(stop_temp)

    is_match_condition = match_condition(start,stop,tt_frame,paths,min_lcm)
    if  is_match_condition:
        return start, stop, counter
    else:
        return find_match_start(tt_frame, paths, min_lcm, counter)