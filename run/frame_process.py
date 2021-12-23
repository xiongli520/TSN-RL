from run.simple_frame_data import simple_frames

def Vl_counter(frames):
    '''
    :param frame: 网络中需要调度的帧信息 ，具体格式看文件frame_data 
    :return: 统计有多少条虚拟链路
    '''
    emp_set = set()
    for i in range(len(frames)):
        for j in frames[i][2]:
            emp_set.add(j)
    return len(emp_set)

def End_counter(frames):
    '''
    :param frame:网络中需要调度的帧信息，具体格式看文件frame_data 
    :return: 统计有多少个终端系统
    '''
    emp_set = set()
    for i in range(len(frames)):
        emp_set.add(frames[i][3])

    return len(emp_set)

def num_frame_eachVL(frames):
    '''
    用来统计网络中帧信息中，各个虚拟链路中消息的个数
    :param frame: 网络中需要调度的帧信息，具体格式看文件frame_data 
    :return: 统计各个虚拟链路中各个消息的个数
    '''
    vl_num = Vl_counter(frames)
    num_frame_eachVL_list = []
    for i in range(vl_num):
        count = 0
        for j in range(len(frames)):
            if i in frames[j][2]:
                count += 1
        num_frame_eachVL_list.append(count)

    return num_frame_eachVL_list

def length_frame_eachVL_list(frames):
    '''
    用来统计网络中帧信息中，各个虚拟链路中消息的长度
    :param frame: 网络中需要调度的帧信息，具体格式看文件frame_data 
    :return: 统计各个虚拟链路中各个消息的长度,并返回最大帧长度
    '''
    maxlen = 0
    vl_num = Vl_counter(frames)
    length_frame_eachVL_list = []
    for i in range(vl_num):  # range(62)
        length = 0
        for j in range(len(frames)):  # range(1050)
            if i in frames[j][2]:  # frame[j][2] => frame 的路径列表
                length += frames[j][0] * 16000000. / frames[j][1]
        length_frame_eachVL_list.append(length)
        if maxlen < length:
            maxlen = length

    return length_frame_eachVL_list,maxlen

def process(tt_frames):
    '''
    把时间划分为小格子62行，1600列
    :param tt_frames: 
    :return: 
    '''
    for i in range(len(tt_frames)):
        tt_frames[i][0] /= 1000
        tt_frames[i][0] = round(tt_frames[i][0])
        tt_frames[i][1] /= 1000
    return tt_frames

def frame_preprocess(frames):

    frames = sorted(frames, key=lambda x: (x[0] * 1. / x[1]), reverse=True)
    end_num = End_counter(frames)
    num_frame_eachVL_list = num_frame_eachVL(frames)
    len_frame_eachVL_list,maxlen = length_frame_eachVL_list(frames)

    return frames, end_num, num_frame_eachVL_list, len_frame_eachVL_list, maxlen



# frames, end_num, num_frame_eachLk_list, len_frame_eachLk_list, maxlen = frame_preprocess(frames)
frames, end_num, num_frame_eachLk_list, len_frame_eachLk_list, maxlen = frame_preprocess(simple_frames)
