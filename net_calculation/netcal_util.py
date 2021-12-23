import numpy as np

def sort_path(paths):
    '''
    对当前调度表进行从小到大排序
    :param paths: 当前调度表
    :return: path_sort:[start_time,stop_tim]只包含吊度表的开始和结束时刻
    '''
    paths_sort = []
    for i in range(len(paths)):
        path_sort_i = []
        for j in range(len(paths[i])):
            path_sort_i.append([paths[i][j][0],paths[i][j][1]])     #只包含调度表的开始时刻和结束时刻
            if paths[i][j][1] > 16000000:
                print(i,j)
                print(paths[i][j])
        sort_temp = sorted(path_sort_i,key=lambda x:x[0])
        paths_sort.append(sort_temp)
    return paths_sort

def bite2us(tt_list,C):
    '''
    将帧长度转化为时间，
    :param tt_list: 一条凌辱的调度表(帧长度)
    :param C: 链路传输速率(Mb/s)
    :return: 返回为时刻表
    '''
    if tt_list == []:
        return []
    else:
        temp = []
        for i in range(len(tt_list)):
            temp_i = []
            for j in range(len(tt_list[i])):
                temp_i.append(tt_list[i][j] / float(C))
            temp.append(temp_i)
        return temp

def arrive_curve(rho,sigma):
    '''
    得到该链路各个rc流量的rho和sigma,   
    :param rho: rho = length/T_BAG, 
    :param sigma: sigma = length
    :return: 根据确定网络演算的到达曲线计算，将它们相加，得到到达曲线
    
    alpha = sum(rho) * t + sum(sigma)
        
    '''
    return np.sum(rho), np.sum(sigma)

def arrive_curse_transform(one_rc_list,previous_max_delay,C):
    '''
    前一条链路发送的消息发送到后一个链路中，会对后面消息的端到端延迟产生影响
    :param rc_list: 前一链路的发送的rc消息信息[rho,sigma,VL]
    :param previous_max_delay: 前一链路的rc最大延迟
    :return: 修改后的alpha曲线参数，相当于改变了这个rc的信息
    '''

    if previous_max_delay == 0:
        J = 0
    else:
        J = previous_max_delay - one_rc_list[1] / C
    rho_transform = one_rc_list[0]
    sigma_transform = one_rc_list[1] + J * rho_transform
    rho, sigma = arrive_curve(rho_transform, sigma_transform)
    rc_list = [rho,sigma]
    return rc_list

