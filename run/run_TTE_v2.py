# from env_tt.env_v1 import env
import time

import numpy as np
import tensorflow as tf

from env_tt.env_v4 import env
from run import DDPG_v2 as DDPG
from run.frame_process import frames

np.random.seed(1)
################## hyper parameter ###################
MAX_EPISODES = 1000
MAX_EP_STEPS = 200
LR_A = 0.01        # learning rate actor
LR_C = 0.01        # learning rate critic
MEMORY_CAPACITY = 1000
BATCH_SIZE = 500
GAMMA = 0.9     # reward discount
REPLACMENT = 10

################# env hyper parameter ################
ACTION_DIM = 1
ACTION_SPACE = [0, 13.518]
OBSERVATION_DIM = 995
TT_FRAMES = frames
PATHS = [[], [], [], [], [], [], [], [], [], [],
                 [], [], [], [], [], [], [], [], [], [],
                 [], [], [], [], [], [], [], [], [], [],
                 [], [], [], [], [], [], [], [], [], [],
                 [], [], [], [], [], [], [], [], [], [],
                 [], [], [], [], [], [], [], [], [], [], [], []]
MIN_LCM = 16000000
C = 100

if __name__ == '__main__':
    sess = tf.Session()

    env_tt = env(ACTION_DIM, ACTION_SPACE, OBSERVATION_DIM, TT_FRAMES, PATHS, MIN_LCM, C)
    actor = DDPG.Actor(sess, ACTION_DIM, ACTION_SPACE, OBSERVATION_DIM,  LR_A, REPLACMENT)
    critic = DDPG.Critic(sess, OBSERVATION_DIM, ACTION_DIM, LR_C, GAMMA, REPLACMENT, actor.a, actor.a_)
    actor.add_grad_to_graph(critic.a_grads)

    sess.run(tf.global_variables_initializer())

    M = DDPG.Memory(MEMORY_CAPACITY, dims= 2*OBSERVATION_DIM + ACTION_DIM + 1)
    t1 = time.time()
    for i in range(MAX_EPISODES):
        # rand_1050 = list(range(1050))
        # random.shuffle(rand_1050)
        # print(rand_1050)
        # s = env_tt.reset(rand_1050)
        s = env_tt.reset()
        ep_reward = 0
        j = 0

        t2 = time.time()
        done = False

        while done == False:
            a = actor.choose_action(s)
            a_exp = np.exp(a)
            # s_, r, done, a_eff = env_tt.step(a_exp, rand_1050)
            s_, r, done, a_eff = env_tt.step(a_exp)
            j += 1
            if r == -500:
                print('循环截止次数：',j)
                break
            else:
                M.store_transition(s, a_eff, r, s_)

                if M.pointer > MEMORY_CAPACITY:
                    b_M = M.sample(BATCH_SIZE)
                    b_s = b_M[:, :OBSERVATION_DIM]
                    b_a = b_M[:, OBSERVATION_DIM:OBSERVATION_DIM + ACTION_DIM]
                    b_r = b_M[:, -OBSERVATION_DIM - 1:-OBSERVATION_DIM]
                    b_s_ = b_M[:, -OBSERVATION_DIM:]

                    critic.learn(b_s, b_a, b_r, b_s_)
                    # q_check, a_check = critic.check(b_s, b_a, b_r, b_s_)
                    actor.learn(b_s)

                s = s_
                ep_reward += r
                print('运行次数j:', j, end='      ')
                print('a:', a, '    a_eff:    ', a_eff, '    reward:   ', r)
                # if done == True:
                #     paths_pro = plot_utils.paths_process(env_tt.paths)
                #     plot_utils.plot_paths(paths_pro)
        print("episodes:    ", i+1, end='     ')
        print('ep_reward:   ', ep_reward)
        #print(' finished time:', time.time() - t2)

    #print('Running time:', time.time() - t1)

