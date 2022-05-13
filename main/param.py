import argparse

parser = argparse.ArgumentParser(description = 'parameter_TSNRL')

#网络结构生成参数

parser.add_argument('--seed', type=int, default=38, help='random seed (default:38)')
parser.add_argument('--tt_flow_cycles', type=int, default=[128, 256, 512, 1024], help='tt flow cycle(ms)')
parser.add_argument('--global_cycle', type=int, default=1024, help='all tt period')

parser.add_argument('--tt_num', type=int, default=20, help='tt flow number')
parser.add_argument('--node_num', type=int, default=10, help='node number')
parser.add_argument('--end_num', type=int, default=8, help='end node number')
parser.add_argument('--switch_num', type=int, default=2, help='switch node number')

parser.add_argument('--pkt_len_min', type=int, default=72, help='pkt length min')
parser.add_argument('--pkt_len_max', type=int, default=1526, help='pkt length max')
parser.add_argument('--delay_min', type=int, default=2048, help='pkt length min')
parser.add_argument('--delay_max', type=int, default=4096, help='pkt length max')


parser.add_argument('--learning_rate', type=float, default=0.001, help='learning rate')
parser.add_argument('--gamma', type=float, default=0.98, help='gamma')

parser.add_argument('--action_size', type=int, default=16, help='action size')
parser.add_argument('--buffer_limit', type=int, default=20000, help='buffer limit')
parser.add_argument('--batch_size', type=int, default=32, help='batch size')

args = parser.parse_args()
