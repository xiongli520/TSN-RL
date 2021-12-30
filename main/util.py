from main.param import *
import numpy as np

def get_tt_flows_length(tt_flows):
    '''
    通过tt_flow信息找到tt流长度集合
    :param tt_flows: 
    :return: 
    '''
    tt_flows_length = []
    if tt_flows:
        for flow in tt_flows.values():
            tt_flows_length.append(flow['pkt_len'])
        return tt_flows_length
    else:
        print('get_tt_flows_length ERROR！！！')
        return [-1]

def get_slot_length(tt_flows):
    '''
    通得到最大最小的帧长度来确定时隙的时间单位长度
    :param tt_flows: 
    :return: 
    '''

    global_cycle = args.global_cycle
    tt_flows_length = get_tt_flows_length(tt_flows)
    max_length = max(tt_flows_length)
    min_length = min(tt_flows_length)

    max_slot_num = global_cycle//max_length
    min_slot_num = global_cycle//min_length

    mid_slot_num = (max_slot_num + min_slot_num)//2

    mid_slot_length = global_cycle // mid_slot_num

    return mid_slot_length

# Action 0
def SPT(tt_schedule_matrix):
    '''
    选择传输时间最短的tt流
    :param tt_schedule_matrix: 当前tt流处理时间
    :return: 选择的tt流序号
    '''
    result = np.full(tt_schedule_matrix.shape[0],fill_value=9999.)
    for i in range(tt_schedule_matrix.shape[0]):
        for j in range(tt_schedule_matrix.shape[1]):
            if tt_schedule_matrix[i][j] != 0:
                result[i] = tt_schedule_matrix[i][j]
                break
    min_idexs = np.where(result == np.min(result))
    if min_idexs[0].size == 1:
        return int(min_idexs[0][0])
    else:
        return int(np.random.choice(min_idexs[0], 1))

# Action 1
def LPT(tt_schedule_matrix):
    '''
    选择传输时间最长的tt流
    :param tt_schedule_matrix: 当前tt流处理时间
    :return: 选择的tt流序号
    '''
    result = np.zeros(tt_schedule_matrix.shape[0])
    for i in range(tt_schedule_matrix.shape[0]):
        for j in range(tt_schedule_matrix.shape[1]):
            if tt_schedule_matrix[i][j] != 0:
                result[i] = tt_schedule_matrix[i][j]
                break
    max_idexs = np.where(result == np.max(result))
    if max_idexs[0].size == 1:
        return int(max_idexs[0][0])
    else:
        return int(np.random.choice(max_idexs[0], 1))

# Action 2
def LWKR(tt_schedule_matrix):
    '''
    选择剩余传输时间最短的tt流
    :param tt_schedule_matrix: 当前的tt流处理时间
    :return: 选择的tt流序号
    '''
    sum_temp = np.sum(tt_schedule_matrix, axis=1)
    min_idexs = np.where(sum_temp == np.min(sum_temp))
    if np.min(sum_temp) == 0:
        for i in min_idexs:
            sum_temp[i] = 9999

    min_idexs = np.where(sum_temp == np.min(sum_temp))
    if min_idexs[0].size == 1:
        return int(min_idexs[0][0])
    else:
        return int(np.random.choice(min_idexs[0], 1))

# Action 3
def MWKR(tt_schedule_matrix):
    '''
    选择剩余传输时间最长的tt流
    :param tt_schedule_matrix: 当前的tt流处理时间
    :return: 选择的tt流序号
    '''

    sum_temp = np.sum(tt_schedule_matrix, axis=1)
    max_idexs = np.where(sum_temp == np.max(sum_temp))
    if max_idexs[0].size == 1:
        return int(max_idexs[0][0])
    else:
        return int(np.random.choice(max_idexs[0], 1))

# Action 4
def SPT_TWK_rate(tt_schedule_matrix, origin_tt_schedule_matrix):
    '''
    工序加工时间与总加工时间比值最小的工件
    :param tt_schedule_matrix: 
    :param origin_tt_schedule_matrix: 
    :return: 
    '''
    result_tt = np.full(tt_schedule_matrix.shape[0], fill_value=9999.)
    for i in range(tt_schedule_matrix.shape[0]):
        for j in range(tt_schedule_matrix.shape[1]):
            if tt_schedule_matrix[i][j] != 0:
                result_tt[i] = tt_schedule_matrix[i][j]
                break
    sum_temp = np.sum(origin_tt_schedule_matrix, axis=1)
    result = result_tt/sum_temp
    min_idexs = np.where(result == np.min(result))
    if min_idexs[0].size == 1:
        return int(min_idexs[0][0])
    else:
        return int(np.random.choice(min_idexs[0], 1))

# Action 5
def LPT_TWK_rate(tt_schedule_matrix, origin_tt_schedule_matrix):
    '''
    工序加工时间与总加工时间比值最小的工件
    :param tt_schedule_matrix: 
    :param origin_tt_schedule_matrix: 
    :return: 
    '''
    result_tt = np.zeros(tt_schedule_matrix.shape[0])
    for i in range(tt_schedule_matrix.shape[0]):
        for j in range(tt_schedule_matrix.shape[1]):
            if tt_schedule_matrix[i][j] != 0:
                result_tt[i] = tt_schedule_matrix[i][j]
                break
    sum_temp = np.sum(origin_tt_schedule_matrix, axis=1)
    result = result_tt/sum_temp
    max_idexs = np.where(result == np.max(result))
    if max_idexs[0].size == 1:
        return int(max_idexs[0][0])
    else:
        return int(np.random.choice(max_idexs[0], 1))

# Action 6
def SPT_TWKR_rate(tt_schedule_matrix):
    '''
    工序加工时间与剩余加工时间比值最小的工件
    :param tt_schedule_matrix: 
    :return: 
    '''
    result_tt = np.full(tt_schedule_matrix.shape[0], fill_value=9999.)
    for i in range(tt_schedule_matrix.shape[0]):
        for j in range(tt_schedule_matrix.shape[1]):
            if tt_schedule_matrix[i][j] != 0:
                result_tt[i] = tt_schedule_matrix[i][j]
                break
    sum_temp = np.sum(tt_schedule_matrix, axis=1)

    result = np.full(tt_schedule_matrix.shape[0], fill_value=9999.)
    for i in range(tt_schedule_matrix.shape[0]):
        if sum_temp[i] != 0:
            result[i] = result_tt[i]/sum_temp[i]

    min_idexs = np.where(result == np.min(result))
    if min_idexs[0].size == 1:
        return int(min_idexs[0][0])
    else:
        return int(np.random.choice(min_idexs[0], 1))

# Action 7
def LPT_TWKR_rate(tt_schedule_matrix):
    '''
    工序加工时间与剩余加工时间比值最大的工件
    :param tt_schedule_matrix: 
    :return: 
    '''
    result_tt = np.zeros(tt_schedule_matrix.shape[0])
    for i in range(tt_schedule_matrix.shape[0]):
        for j in range(tt_schedule_matrix.shape[1]):
            if tt_schedule_matrix[i][j] != 0:
                result_tt[i] = tt_schedule_matrix[i][j]
                break
    sum_temp = np.sum(tt_schedule_matrix, axis=1)

    result = np.zeros(tt_schedule_matrix.shape[0])
    for i in range(tt_schedule_matrix.shape[0]):
        if sum_temp[i] != 0:
            result[i] = result_tt[i] / sum_temp[i]

    max_idexs = np.where(result == np.max(result))
    if max_idexs[0].size == 1:
        return int(max_idexs[0][0])
    else:
        return int(np.random.choice(max_idexs[0], 1))

# Action 8
def SPT_TWK_muti(tt_schedule_matrix, origin_tt_schedule_matrix):
    '''
    工序加工时间与总加工时间乘积最小的工件
    :param tt_schedule_matrix: 
    :param origin_tt_schedule_matrix: 
    :return: 
    '''
    result_tt = np.full(tt_schedule_matrix.shape[0], fill_value=9999.)
    for i in range(tt_schedule_matrix.shape[0]):
        for j in range(tt_schedule_matrix.shape[1]):
            if tt_schedule_matrix[i][j] != 0:
                result_tt[i] = tt_schedule_matrix[i][j]
                break
    sum_temp = np.sum(origin_tt_schedule_matrix, axis=1)
    result = result_tt*sum_temp
    min_idexs = np.where(result == np.min(result))
    if min_idexs[0].size == 1:
        return int(min_idexs[0][0])
    else:
        return int(np.random.choice(min_idexs[0], 1))

# Action 9
def LPT_TWK_muti(tt_schedule_matrix, origin_tt_schedule_matrix):
    '''
    工序加工时间与总加工时间乘积最大的工件
    :param tt_schedule_matrix: 
    :param origin_tt_schedule_matrix: 
    :return: 
    '''
    result_tt = np.zeros(tt_schedule_matrix.shape[0])
    for i in range(tt_schedule_matrix.shape[0]):
        for j in range(tt_schedule_matrix.shape[1]):
            if tt_schedule_matrix[i][j] != 0:
                result_tt[i] = tt_schedule_matrix[i][j]
                break
    sum_temp = np.sum(origin_tt_schedule_matrix, axis=1)
    result = result_tt*sum_temp
    max_idexs = np.where(result == np.max(result))
    if max_idexs[0].size == 1:
        return int(max_idexs[0][0])
    else:
        return int(np.random.choice(max_idexs[0], 1))

# Action 10
def SPT_TWKR_muti(tt_schedule_matrix):
    '''
    工序加工时间与剩余加工时间乘积最小的工件
    :param tt_schedule_matrix: 
    :return: 
    '''
    result_tt = np.full(tt_schedule_matrix.shape[0], fill_value=9999.)
    for i in range(tt_schedule_matrix.shape[0]):
        for j in range(tt_schedule_matrix.shape[1]):
            if tt_schedule_matrix[i][j] != 0:
                result_tt[i] = tt_schedule_matrix[i][j]
                break
    sum_temp = np.sum(tt_schedule_matrix, axis=1)
    result = (sum_temp+1)*result_tt
    min_idexs = np.where(result == np.min(result))
    if min_idexs[0].size == 1:
        return int(min_idexs[0][0])
    else:
        return int(np.random.choice(min_idexs[0], 1))

# Action 11
def LPT_TWKR_muti(tt_schedule_matrix):
    '''
    工序加工时间与剩余加工时间乘积最大的工件
    :param tt_schedule_matrix: 
    :return: 
    '''
    result_tt = np.zeros(tt_schedule_matrix.shape[0])
    for i in range(tt_schedule_matrix.shape[0]):
        for j in range(tt_schedule_matrix.shape[1]):
            if tt_schedule_matrix[i][j] != 0:
                result_tt[i] = tt_schedule_matrix[i][j]
                break
    sum_temp = np.sum(tt_schedule_matrix, axis=1)
    result = sum_temp*result_tt
    max_idexs = np.where(result == np.max(result))
    if max_idexs[0].size == 1:
        return int(max_idexs[0][0])
    else:
        return int(np.random.choice(max_idexs[0], 1))

# Action 12
def LSO(tt_schedule_matrix):
    '''
    除了当前动作外，所剩时间最长的tt流
    :param tt_schedule_matrix: 
    :return: 
    '''
    result_tt = np.ones(tt_schedule_matrix.shape[0])
    for i in range(tt_schedule_matrix.shape[0]):
        for j in range(tt_schedule_matrix.shape[1]):
            if tt_schedule_matrix[i][j] != 0:
                result_tt[i] = tt_schedule_matrix[i][j]
                break
    sum_temp = np.sum(tt_schedule_matrix, axis=1)
    result = sum_temp - result_tt
    max_idexs = np.where(result == np.max(result))
    if max_idexs[0].size == 1:
        return int(max_idexs[0][0])
    else:
        return int(np.random.choice(max_idexs[0], 1))

# Action 13
def SSO(tt_schedule_matrix):
    '''
    除了当前动作外，所剩时间最短的tt流
    :param tt_schedule_matrix: 
    :return: 
    '''
    result_tt = np.full(tt_schedule_matrix.shape[0], fill_value=-0.5)
    for i in range(tt_schedule_matrix.shape[0]):
        for j in range(tt_schedule_matrix.shape[1]):
            if tt_schedule_matrix[i][j] != 0:
                result_tt[i] = tt_schedule_matrix[i][j]
                break
    sum_temp = np.sum(tt_schedule_matrix, axis=1)
    result = sum_temp - result_tt
    for i in range(len(result)):
        if result[i] == 0.5:
            result[i] = 9999.

    min_idexs = np.where(result == np.min(result))
    if min_idexs[0].size == 1:
        return int(min_idexs[0][0])
    else:
        return int(np.random.choice(min_idexs[0], 1))

# Action 14
def SRM(tt_schedule_matrix, tt_route_matrix):
    '''
    除了当前状态下的，剩余的最短的链路剩余时间，的tt流
    :param tt_schedule_matrix: tt流调度处理时间矩阵
    :param tt_route_matrix: tt流路由矩阵
    :return: 
    '''
    # 链路数目
    link_num = np.max(tt_route_matrix) + 1
    link2time = np.zeros(int(link_num))
    # 记录链路剩余需要消息的处理总时间
    for i in range(tt_schedule_matrix.shape[0]):
        for j in range(tt_schedule_matrix.shape[1]):
            link2time[int(tt_route_matrix[i][j])] += tt_schedule_matrix[i][j]

    # 记录各个tt流当前的处理时间和当前的路由链路
    result_tt = np.zeros(tt_schedule_matrix.shape[0])
    result_route = np.full(tt_schedule_matrix.shape[0], fill_value=-1)
    for i in range(tt_schedule_matrix.shape[0]):
        for j in range(tt_schedule_matrix.shape[1]):
            if tt_schedule_matrix[i][j] != 0:
                result_tt[i] = tt_schedule_matrix[i][j]
                result_route[i] = tt_route_matrix[i][j]
                break
    result = np.full(tt_schedule_matrix.shape[0], fill_value=9999.)
    for i in range(tt_schedule_matrix.shape[0]):
        if result_route[i] != -1 and result_tt[i] != 0:
            result[i] = link2time[int(result_route[i])] - result_tt[i]

    min_idexs = np.where(result == np.min(result))
    if min_idexs[0].size == 1:
        return int(min_idexs[0][0])
    else:
        return int(np.random.choice(min_idexs[0], 1))

# Action 15
def LRM(tt_schedule_matrix, tt_route_matrix):
    '''
    除了当前状态下的，剩余的最长的链路剩余时间，的tt流
    :param tt_schedule_matrix: tt流调度处理时间矩阵
    :param tt_route_matrix: tt流路由矩阵
    :return: 
    '''
    # 链路数目
    link_num = np.max(tt_route_matrix) + 1
    link2time = np.zeros(int(link_num))
    # 记录链路剩余需要消息的处理总时间
    for i in range(tt_schedule_matrix.shape[0]):
        for j in range(tt_schedule_matrix.shape[1]):
            link2time[int(tt_route_matrix[i][j])] += tt_schedule_matrix[i][j]

    # 记录各个tt流当前的处理时间和当前的路由链路
    result_tt = np.zeros(tt_schedule_matrix.shape[0])
    result_route = np.full(tt_schedule_matrix.shape[0], fill_value=-1)
    for i in range(tt_schedule_matrix.shape[0]):
        for j in range(tt_schedule_matrix.shape[1]):
            if tt_schedule_matrix[i][j] != 0:
                result_tt[i] = tt_schedule_matrix[i][j]
                result_route[i] = tt_route_matrix[i][j]
                break
    result = np.full(tt_schedule_matrix.shape[0], fill_value=-1.)
    for i in range(tt_schedule_matrix.shape[0]):
        if result_route[i] != -1 and result_tt[i] != 0:
            result[i] = link2time[int(result_route[i])] - result_tt[i]

    max_idexs = np.where(result == np.max(result))
    if max_idexs[0].size == 1:
        return int(max_idexs[0][0])
    else:
        return int(np.random.choice(max_idexs[0], 1))


if __name__ == '__main__':
    # tt_schedule_matrix = np.array([[64., 64.,  0.],
    #                                 [ 51.,51.,  0.],
    #                                 [ 42. ,42., 42.],
    #                                 [ 49. ,49., 49.],
    #                                 [35. ,35.,  0.],
    #                                 [56. ,56., 56.],
    #                                 [ 35. , 35.,  35.],
    #                                 [44. ,44., 44.],
    #                                 [58. ,58., 58.],
    #                                 [43. ,43., 43.],
    #                                 [ 36. ,36., 36.],
    #                                 [ 0. , 64., 64.],
    #                                 [ 59. , 0.,  0.],
    #                                 [35. ,35.,  0.],
    #                                 [ 33.,33.,  0.],
    #                                 [ 0. , 0.,  0.],
    #                                 [ 58. , 58., 58.],
    #                                 [ 48. , 48., 48.],
    #                                 [ 33. , 33., 33.],
    #                                 [ 51. , 51., 51.],])
    tt_schedule_matrix = np.array([[0., 0., 0.],
                                   [0., 0., 0.],
                                   [0., 0., 0.],
                                   [0., 0., 49.],
                                   [0., 0., 0.],
                                   [0., 0., 0.],
                                   [0., 0., 0.],
                                   [0., 0., 0.],
                                   [0., 0., 0.],
                                   [0., 0., 43.],
                                   [0., 0., 0.],
                                   [0., 0., 0.],
                                   [0., 0., 0.],
                                   [0., 0., 0.],
                                   [0., 0., 0.],
                                   [0., 0., 0.],
                                   [0., 0., 0.],
                                   [0., 0., 0.],
                                   [0., 0., 0.],
                                   [0., 0., 0.], ])
    tt_route_matrix = np.array([[ 0., 11.,  0.],
                                [ 2.,  9.,  0.],
                                [ 5.,17.,  8.],
                                [ 7., 17., 10.],
                                [ 5., 16.,  0.],
                                [ 2., 12., 15.],
                                [ 3.,  8.,  0.],
                                [ 3., 12., 16.],
                                [ 0., 12., 16.],
                                [ 6., 17., 10.],
                                [ 4., 17.,  9.],
                                [ 4., 17., 11.],
                                [ 2.,  0.,  0.],
                                [ 7., 17.,  0.],
                                [ 0.,  9.,  0.],
                                [ 3.,  0.,  0.],
                                [ 6., 17., 10.],
                                [ 6., 17., 9.],
                                [ 2., 12., 16.],
                                [ 0., 12., 14.],])

    # print(LRM(tt_schedule_matrix,tt_route_matrix))
    print(LSO(tt_schedule_matrix))


