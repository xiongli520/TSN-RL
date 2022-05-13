from Data.DASP.Stream_Partition import *
import copy
from test.util import *

class Local_Search:
    def __init__(self, tt_flows, group_num):
        self.tt_flows = tt_flows
        self.tt_num = len(tt_flows)
        self.group_num = group_num
        self.doc_graph = DoC_Graph(self.tt_flows)
        self.stream_partition = Stream_Partition(self.doc_graph, self.group_num)
        self.paths_id = self.get_paths_index(self.tt_flows)
        self.paths_len = self.get_paths_len(self.tt_flows)
        # self.local_find()

    def get_paths_index(self, tt_flows):
        paths_id = []
        for i in range(self.tt_num):
            paths_id.append(tt_flows[str(i)]['path_id'])
        return paths_id

    def get_paths_len(self, tt_flows):
        paths_len = []
        for i in range(self.tt_num):
            paths_len.append(len(tt_flows[str(i)]['paths']))
        return paths_len

    def local_find(self):
        messages = set()
        for i in range(self.tt_num):
            messages.add(i)
        while len(messages) != 0:
            stream_id, contribution = self.find_max_contribution_stream_id(self.doc_graph, messages)
            if stream_id in messages:
                messages.remove(stream_id)
            tt_flows = copy.deepcopy(self.tt_flows)
            tt_flow = tt_flows[str(stream_id)]
            path_id = tt_flow['path_id']
            path_len = self.paths_len[stream_id]
            for j in range(path_len):
                if path_id != j:
                    tt_flows[str(stream_id)]['path_id'] = j
                    doc_graph = DoC_Graph(tt_flows)
                    tmp = self.get_contribution(stream_id, doc_graph)
                    if contribution > tmp:
                        contribution = tmp
                        self.tt_flows[str(stream_id)]['path_id'] = j

    def find_max_contribution_stream_id(self, doc_graph, messages):
        # stream_id = 0
        contribution = float('inf')
        for i in messages:
            if contribution > self.get_contribution(i, doc_graph):
                contribution = self.get_contribution(i, doc_graph)
                stream_id = i
        return stream_id, contribution

    def get_contribution(self, stream_id, doc_graph):
        contribution = 0
        for i in range(self.tt_num):
            if i != stream_id:
                contribution += doc_graph.adj_mat[stream_id][i]
        return contribution

    def get_stream_partition(self):
        self.doc_graph = DoC_Graph(self.tt_flows)
        self.stream_partition = Stream_Partition(self.doc_graph, self.group_num)
        return self.stream_partition


if __name__ == '__main__':
    fo_network_info = open("../resource/info/network_info.txt", "r")
    fo_node_info = open("../resource/info/node_info.txt", "r")
    node_num = int(fo_network_info.readline())
    node_num_ = int(fo_node_info.readline())
    edge_num = int(fo_network_info.readline())
    graph = Graph(node_num)
    for i in range(edge_num):
        ss = fo_network_info.readline()
        node1_index, node2_index = map(int, ss.split())
        graph.add_edge(node1_index, node2_index)
    for i in range(node_num_):
        index, is_end_node, is_switch_node = map(int, fo_node_info.readline().split())
        if is_end_node == 1:
            graph.nodes[index].set_end_node()
        if is_switch_node == 1:
            graph.nodes[index].set_switch_node()

    fo_node_info.close()
    fo_network_info.close()

