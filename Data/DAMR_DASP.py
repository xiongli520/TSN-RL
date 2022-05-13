from Data.DAMR.Damr import *
from Data.DASP.Stream_Partition import *

def DAMR_DASP(tt_flows, max_iteration, group_num):
    '''
    通过输入tt流，利用DAMR和DASP方法对流进行预处理
    :param tt_flows:
    :param max_iteration: DAMR的迭代次数
    :param group_num: DASP分组个数
    :return:
    '''
    da = Damr(tt_flows, max_iteration, group_num)
    da.damr()
    da.write_to_file()
    tt_flows = da.tt_flows
    doc_graph = DoC_Graph(tt_flows)
    stream_partition = Stream_Partition(doc_graph, group_num)
    return stream_partition.groups_final


