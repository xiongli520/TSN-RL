from Data.Graph import *

def dijkstra(graph, src):
    length = len(graph)

    for i in range(length):
        for j in range(length):
            if graph[i][j] == 0:
                graph[i][j] = 999
    nodes = [i for i in range(length)]

    visited = [src]
    path = {src:{src:[]}}
    nodes.remove(src)
    distance_graph = {src:0}
    pre = next = src

    while nodes:
        distance = float('inf')
        for v in visited:
             for d in nodes:
                new_dist = graph[src][v] + graph[v][d]
                if new_dist < distance:
                    distance = new_dist
                    next = d
                    pre = v
                    graph[src][d] = new_dist


        path[src][next] = [i for i in path[src][pre]]
        path[src][next].append(next)

        distance_graph[next] = distance

        visited.append(next)
        nodes.remove(next)

    return distance_graph, path

class Route:
    def __init__(self, graph):
        self.graph = graph
        self.node_num = graph.node_num
        self.path = []
        self.paths = []


    def is_connectable(self, start, end):
        '''
        判断两个节点是否能连通
        :param start:
        :param end:
        :return:
        '''
        queue = []
        visited = []
        queue.append(start)
        while len(queue)!=0:
            for i in range(self.node_num):
                if self.graph.adj_mat[start][i]==1 and i not in visited:
                    queue.append(i)

            if end in queue:
                return True
            else:
                visited.append(queue[0])
                queue.pop(0)
                if(len(queue)!=0):
                    start = queue[0]

        return False

    def get_adj_unvisited_node(self, v):
        '''
        与节点v相邻，并且这个节点没有被访问到，并且这个节点不在栈中
        :param v:
        :return:
        '''

        arr = self.graph.nodes[v].all_visited_list
        for i in range(self.node_num):
            if self.graph.adj_mat[v][i] == 1 and arr[i] == 0 and i not in self.path:
                self.graph.nodes[v].set_visited(i)
                return i
        return -1

    def get_path(self, start, end):
        '''
        得到从start到end的所有路径
        :param start:
        :param end:
        :return:
        '''
        self.paths = []
        if not self.is_connectable(start, end):
            print('节点之间没有通路')
        else:
            self.cal_paths(start,end)
        return self.paths

    def cal_paths(self, start, end):
        self.graph.nodes[start].set_was_visited(True)
        self.path.append(start)

        while len(self.path)!=0:
            v = self.get_adj_unvisited_node(self.path[-1])
            if v==-1:
                tmp = []
                for i in range(self.node_num):
                    tmp.append(0)
                self.graph.nodes[self.path[-1]].set_all_visited_list(tmp)
                self.path.pop()
            else:
                self.path.append(v)

            if len(self.path)!=0 and end == self.path[-1]:
                self.graph.nodes[end].set_was_visited(False)
                self.paths.append((self.path.copy()))
                self.path.pop()
        return self.paths


if __name__ == '__main__':
    # graph_list = [[0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    #              [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    #              [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    #              [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    #              [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    #              [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    #              [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    #              [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    #              [1, 1, 1, 1, 0, 0, 0, 0, 0, 1],
    #              [0, 0, 0, 0, 1, 1, 1, 1, 1, 0]]
    #
    #
    #
    # distance, path = dijkstra(graph_list, 2)
    # print(distance, '\n', path)
    fo = open("resource/info/network_info.txt", "r")
    node_num = int(fo.readline())
    # print(type(node_num))
    # print(node_num)
    edge_num = int(fo.readline())
    # print(edge_num)
    graph = Graph(node_num)
    for i in range(edge_num):
        ss = fo.readline()
        node1_index, node2_index = map(int, ss.split())
        graph.add_edge(node1_index, node2_index)
    print(graph.get_all_connection_list())
    print(graph.adj_mat)
    rt = Route(graph)
    print(rt.get_path(0, 7))