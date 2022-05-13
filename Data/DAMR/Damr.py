from Data.DAMR.Local_Search import *
import copy
from test.util import *

class Damr:
    def __init__(self, tt_flows, max_iterations, group_num):
        self.tt_flows = tt_flows
        self.tt_num = len(tt_flows)
        self.max_iterations = max_iterations
        self.group_num = group_num
        self.doc_graph = DoC_Graph(self.tt_flows)
        self.stream_partition = Stream_Partition(self.doc_graph, self.group_num)
        self.n_cgc = self.stream_partition.nCGC_final
        self.n_cgc_final = 0

    def damr(self):
        '''
        利用局部迭代，优化分组
        :return:
        '''
        n_cgc = self.n_cgc
        for i in range(self.max_iterations):
            tt_flows = copy.deepcopy(self.tt_flows)
            tt_flows = self.random_path(tt_flows)
            local_search = Local_Search(tt_flows, self.group_num)
            local_search.local_find()
            stream_partition = local_search.get_stream_partition()
            if stream_partition.nCGC_final<n_cgc:
                n_cgc = stream_partition.nCGC_final
                self.tt_flows = copy.deepcopy(tt_flows)
        self.n_cgc_final = n_cgc

    def random_path(self, tt_flows):
        '''
        随机重置选择的路径
        :return:
        '''
        tt_num = len(tt_flows)
        for i in range(tt_num):
            path_id = random.randint(0, len(tt_flows[str(i)]['paths']) - 1)
            tt_flows[str(i)]['path_id'] = path_id
        return tt_flows

    def write_to_file(self):
        if not os.path.exists('D:\\MyRL\\TSN-RL\\Data\\resource\\info'):
            os.makedirs('D:\\MyRL\\TSN-RL\\Data\\resource\\info')

        if self.tt_flows:
            json.dump(self.tt_flows, open('/Data/resource/unprocess_flow/tt_flows_new.json', "w"), indent=4)


if __name__ == '__main__':
    tt_flows = read_tt_flows_from_file()
    da = Damr(tt_flows, 10, 4)
    da.damr()
    da.write_to_file()