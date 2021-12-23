import net_calculation.netcal_util as netcal_util
import numpy as np

def path_max_delay(tt_list,rc_list,C,i):
    '''
    通过tt和rc消息得到rc消息的最大端到端延迟
    :param tt_list: 链路i的tt消息发送开始和发送结束时刻
    :param rc_list: [[rho, sigma], [rho, sigma], ...],链路i上的rc消息特征
                    rho = length/T_BAG,   sigma = length
    :param C: 链路传输速率
    :param i: 链路编号
    :return: 该链路rc消息的最大延迟
    '''
    if len(rc_list) == 1 and i < 31 and (i % 2) == 0:
        return 0
    elif len(rc_list) == 0:
        return 0
    else:
        [rho,sigma] = np.sum(rc_list,axis=0)
        """
        到达曲线 alpha = w_alpha * t + b_alpha
        """
        w_alpha, b_alpha = netcal_util.arrive_curve(rho, sigma)
        max_delay = max_delay_cal(tt_list,C,b_alpha)
        return max_delay

def max_delay_cal(tt_list,C,b_alpha):
    '''
    通达到曲线参数b_alpha和tt调度表得到rc的最大传输延迟
    :param tt_list: tt发送开始和发送结束时刻表
    :param C: 链路传输速率
    :param b_alpha: 其实就是该连续要传输的rc帧长度
    :return: delay 返回rc的最大端到端延迟
    '''
    x_eff_raw = b_alpha / C
    if tt_list == []:
        delay =  x_eff_raw
        return delay

    x_eff_all = x_eff_raw - tt_list[0][0]
    if x_eff_all < 0:
        return x_eff_raw
    elif x_eff_all == 0:
        return tt_list[0][1]
    else:
        for i in range(1, len(tt_list)):
            x_eff = tt_list[i][0] - tt_list[i-1][1]
            delay = tt_list[i-1][1]
            x_eff_all_res = x_eff_all - x_eff
            if x_eff_all_res < 0:
                return delay + x_eff_all
            elif x_eff_all_res == 0:
                return tt_list[i][1]
            else:
                x_eff_all = x_eff_all_res
    # print(offset_list[-1])
    # print('hei',x_eff_all, x_eff_raw)
    delay = tt_list[-1][1] + x_eff_all
    # return delay
    return delay

def net_calculus(rc_vl, C, paths):
    '''
    返回当前调度表情况下，rc消息的最大端到端延迟
    :param rc_vl: rc消息帧信息[rho,sigma,VL],rho = length/T_BAG,sigma = length,VL:为通过的链路编号列表
    :param C: 链路传输速率100Mb/s
    :param paths: 当前的消息调度表
    :return: rc_delay,返回当前调度表情况下，所有链路的rc消息的最大端到端延迟
    '''
    rc_delay = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]

    tt_lists = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]

    tt_lists_raw = netcal_util.sort_path(paths)         #tt_lists: tt消息的发送开始和发送结束时刻
    for i in range(len(tt_lists_raw)):
        tt_lists[i] = netcal_util.bite2us(tt_lists_raw[i],C)
        rc_delay[i].append(0)

    # E - S
    i = 0
    for i in range(32)[::2]:
        rc_sending_nodes = []
        for j in rc_vl[i]:
            rc_sending_nodes.append(j[:2])
        if len(rc_sending_nodes) == 0:
            rc_sending_nodes.append(0)
        delay = path_max_delay(tt_lists[i],rc_sending_nodes,C,i)
        rc_delay[i][0] += delay

    # S - S
    for m in range(10):
        ''' iteration k times '''
        for i in range(32,62):
            end_delay, source = 0, []
            for j in rc_vl[i]:
                vl_source_num = j[2][0]
                if vl_source_num < 32:
                    source_maxdelay_e = rc_delay[vl_source_num][0]
                    j_tranform = netcal_util.arrive_curse_transform(j,source_maxdelay_e,C)
                    source.append(j_tranform[:2])
                else:
                    source_maxdelay_s = rc_delay[vl_source_num][0]
                    j_tranform = netcal_util.arrive_curse_transform(j,source_maxdelay_s,C)
                    source.append(j_tranform[:2])
            end_delay = path_max_delay(tt_lists[i],source,C,i)
            rc_delay[i][0] = end_delay

    # S - E
    for i in range(1,33)[::2]:
        rc_receiving_nodes = []
        for j in rc_vl[i]:
            vl_source_num = j[2][0]
            source_maxdelay = rc_delay[vl_source_num][0]
            j_tranform = netcal_util.arrive_curse_transform(j,source_maxdelay,C)
            rc_receiving_nodes.append(j_tranform[:2])
        delay = path_max_delay(tt_lists[i],rc_receiving_nodes,C,i)
        rc_delay[i][0] += delay

    return rc_delay

