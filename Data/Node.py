class Node:
    def __init__(self, index, capacity):
        self.id = index
        self.bufferCapacity = capacity
        self.isEndNode = 0
        self.isSourceNode = 0
        self.isSwitchNode = 0
        self.isDestinationNode = 0
        self.connection_list = []

    #     为了路由设置的参数
        self.was_visited = False
        self.all_visited_list = []

    def set_all_visited_list(self, all_visited_list):
        self.all_visited_list = all_visited_list

    def set_was_visited(self, was_visited):
        self.was_visited = was_visited

    def set_visited(self, j):
        if j>len(self.all_visited_list):
            print('node set visited error, out of range...')
        else:
            self.all_visited_list[j] = 1

    def set_source_node(self):
        self.isSourceNode = 1

    def set_destination_node(self):
        self.isDestinationNode = 1

    def set_end_node(self):
        self.isEndNode = 1

    def set_switch_node(self):
        self.isSwitchNode = 1

    def unset_source_node(self):
        self.isSourceNode = 0

    def unset_destination_node(self):
        self.isDestinationNode = 0

    def unset_end_node(self):
        self.isEndNode = 0

    def unset_switch_node(self):
        self.isSwitchNode = 0

    def reset(self):
        self.isEndNode = 0
        self.isSourceNode = 0
        self.isSwitchNode = 0
        self.isDestinationNode = 0