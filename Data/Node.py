class Node:
    def __init__(self, index, capacity):
        self.id = index
        self.bufferCapacity = capacity
        self.isEndNode = 0
        self.isSourceNode = 0
        self.isSwitchNode = 0
        self.isDestinationNode = 0

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