import frame_process
import numpy as np

from run import RC_frames

np.random.seed(1)



rc_length_sum = RC_frames.path_length_sum
rc_single_sum = RC_frames.path_single_sum
path_each_sum = frame_process.len_frame_eachLk_list
path_each_num = frame_process.num_frame_eachLk_list

def state_generation(tt_frame,paths,rest_frame_num,min_lcm):
    '''
    通过输入帧信息tt_frame和未完成的调度表paths等信息得到当前状态State
    :param tt_frame: 选择的单个帧
    :param paths: 调度表
    :param rest_frame_num:剩余的帧个数（包括本身） 
    :param min_lcm: 大周期（最小公倍数）
    :return: state=[9维],分别如下
            length_sum_exist:该帧传输的链路已经存在的帧长度总和
            num_exist:该帧传输的链路已经存在的帧的个数
            rest_frame_num/1050：剩余没有调度的帧的个数
            quantity:在一个min_lcm周期下，传输的个数
            frame_length:该帧的长度
            path_through_num:链路需要传输的帧的总长度
            path_through_sum:链路需要传输帧的总个数
            path_rc_length_sum:链路需要传输的RC消息帧总长度
            path_rc_single_sum:链路需要传输的在单个周期的帧的总长度
    '''
    path_through = []
    for i in tt_frame[2]:
        path_through.append(paths[i])

    #这里只需要该帧的第一条链路传输信息即可，
    #因为确定第一条链路的开始发送时间，那么之后的传输时间就已经确定了
    #所以状态信息完全有第一条链路的信息决定
    if len(path_through[0]) == 0:
        length_sum_exist,num_exist = 0,0
    else:
        length_sum_exist,num_exist = 0,len(path_through[0])
        for j in range(len(path_through[0])):
            length_sum_exist += path_through[0][j][2]

    frame_length = tt_frame[0]
    quantity = min_lcm // tt_frame[1]
    path_through_num = path_each_num[tt_frame[2][0]]
    path_through_sum = path_each_sum[tt_frame[2][0]]
    path_rc_length_sum = rc_length_sum[tt_frame[2][0]]
    path_rc_single_sum = rc_single_sum[tt_frame[2][0]]

    state = [length_sum_exist,num_exist,rest_frame_num/1050.,
             quantity,frame_length,path_through_num,
             path_through_sum,path_rc_length_sum,path_rc_single_sum]
    state =np.array(state)
    state_log = state_process(state)
    return state_log

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

def get_start_stop(a, tt_frame, paths, n=0):
    '''
    通过得到的动作a（也就是帧在第一条链路上发送时刻），得到开始发送start和发送结束stop列表
    :param a: 帧在第一条链路上的发送时刻
    :param tt_frame: 帧信息
    :param paths: 当前调度表
    :param n: 参数（用于调节帧的传输延迟）
    :return: start,stop传输链路的发送开始时刻列表和发送结束时刻列表
    '''
    start, stop=[], []
    for i in range(len(tt_frame[2])):       #tt_frame[2]:表示该帧通过的物理链路列表
        if i == 0:
            start_temp = a
            stop_temp = start_temp + tt_frame[0]
            start.append(start_temp)
            stop.append(stop_temp)
        else:
            start_temp = np.random.randint(3000,min(10000,3001+3000*n/500)) + stop_temp
            stop_temp = start_temp + tt_frame[0]
            start.append(start_temp)
            stop.append(stop_temp)
    return start, stop


def get_match_start(a,tt_frame,paths,n=0):
    '''
    通过得到的动作a（也就是帧在第一条链路上发送时刻），得到合适和开始发送start和发送结束stop列表
    :param a: 帧在第一条链路上的发送时刻
    :param tt_frame: 帧信息
    :param paths: 当前调度表
    :param n: 参数（用于调节帧的传输延迟）
    :return: start,stop传输链路的发送开始时刻列表和发送结束时刻列表
            如果返回为-1，则说明未能找到合适的start和stop
    '''
    start,stop=[],[]
    for i in range(len(tt_frame[2])):       #tt_frame[2]:表示该帧通过的物理链路列表
        if i == 0:
            start_temp = a
            stop_temp = start_temp + tt_frame[0]
            start.append(start_temp)
            stop.append(stop_temp)
        else:
            start_temp = np.random.randint(3000,min(10000,3001+3000*n/500)) + stop_temp
            stop_temp = start_temp + tt_frame[0]
            start.append(start_temp)
            stop.append(stop_temp)

    is_match_condition = match_condition(start, stop, tt_frame, paths, min_lcm=16000000)

    if is_match_condition:
        return start, stop, 1
    else:
        start, stop, co = find_match_start(tt_frame,paths,min_lcm=16000000,counter=0)
        if start == -1:
            print('cant find')
            return -1, -1, -1
        else:
            return start, stop, co

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

def find_match_start(tt_frame,paths,min_lcm,counter):
    '''
    通过某一种手段，必须找到满足条件的start和stop列表
    :param tt_frame: 帧信息
    :param paths: 当前调度表
    :param min_lcm: 周期最小公倍数
    :return: start,stop传输链路的发送开始时刻列表和发送结束时刻列表
            如果返回为-1，则说明未能找到合适的start和stop
    '''
    start,stop = [],[]
    path_through = tt_frame[2]
    counter += 1
    high = np.log(tt_frame[1]-tt_frame[0])
    sample_range = [[0,high/3.],[high/3.,(2*high/3.)],[(2*high/3.),high]]

    if counter > 500:
        return -1,-1,-1
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
        return find_match_start(tt_frame,paths,min_lcm,counter)

def get_tt_delay(start,stop):
    '''
    通过tt消息调度表，得到tt的端到端延迟
    :param start:该帧在vl列表发送开始时刻列表
    :param stop: 该帧在vl列表发送结束时刻列表
    :return: tt_delay 该帧的端到端延迟
    '''
    tt_delay = 0
    for i in range(len(start)-1):
        tt_delay += start[i+1] - stop[i]

    return tt_delay

def get_frame(tt_frames,rest_frame_num):
    '''
    通过当前剩余帧数目判断下一个输入的帧
    :return: 
    '''
    index = len(tt_frames) - rest_frame_num
    return tt_frames[index]

def state_process(state):
    '''
    对state的各个量进行预处理，归一化
    :param state: 
    :return: 
    '''
    state = np.clip(state, 0.00001, max(state))
    state_log = np.log(state)
    state_log[0] -= 12
    state_log[4] -= 10
    state_log[6] -= 15
    state_log[7] -= 13
    state_log[8] -= 11

    return state_log