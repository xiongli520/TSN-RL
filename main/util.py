from main.param import *

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


