from run import frame_process

#import condition
paths = [[],[],[],[],[],[],[],[],[],[],
        [],[],[],[],[],[],[],[],[],[],
        [],[],[],[],[],[],[],[],[],[],
        [],[],[],[],[],[],[],[],[],[],
        [],[],[],[],[],[],[],[],[],[],
        [],[],[],[],[],[],[],[],[],[],[],[]]

min_lcm = 16000000
paths_frames_num = frame_process.num_frame_eachLk_list
paths_frames_len = frame_process.len_frame_eachLk_list

def search(frame,paths,network,sess,rest_frame,frame_i_index,path_i,path_i_frame_num,path_i_frame_len):
    '''
    :param frame: 
    :param paths: 整个网络传输信息的调度表信息
    :param network: nn神经网络
    :param sess: sess为神经网络的会话
    :param rest_frame: 剩下的帧个数
    :param frame_i_index: 此帧通过的链路
    :param path_i: 此帧通过虚拟链路在paths中的信息
    :param path_i_frame_num: 此帧通过链路的帧个数
    :param path_i_frame_len: 此帧通过链路的帧长度（时间单位）
    :return: 
    '''
    start,stop = [],[]
    state_path_i = []           #记录输入nn的状态参数
    quantity = min_lcm // frame[1]
    e2e_delay,delay = 0 ,0
    sendIatime = 3000
    start_temp,stop_temp = 0,0

    for k in range(len(frame_i_index)):
        if path_i[k]==[]:
            length_sum_ed ,num_ed = 0,0
        else:
            length_sum_ed = 0
            num_ed = len(path_i[k])
            for j in range(num_ed):
                length_sum_ed += path_i[k][j][2]


        if k == 0:
            start_temp = sess.run(network.out,feed_dict={network.inputs:nn_input})[0,0]
            state_path_i.append(nn_input)
        else:
            start_temp = sendIatime + stop_temp

        start.append(start_temp)
        stop_temp = start_temp + frame[0]
        stop.append(stop_temp)


if __name__ == '__main__':
    for i in range(len(frame_process.frames)):
        print(frame_process.frames[i])