import numpy as np
import tensorflow as tf

from env_tt.env_v2 import env
from run import A1C
from run.frame_process import frames

################## hyper parameter ###################
MAX_EPISODE = 100
GAMMA = 0.9
LR_A = 0.001
LR_C = 0.01


################# env hyper parameter ################
ACTION_DIM = 1
ACTION_SPACE = [0,13.518]
OBSERVATION_DIM = 9
TT_FRAMES = frames
PATHS = [[], [], [], [], [], [], [], [], [], [],
                 [], [], [], [], [], [], [], [], [], [],
                 [], [], [], [], [], [], [], [], [], [],
                 [], [], [], [], [], [], [], [], [], [],
                 [], [], [], [], [], [], [], [], [], [],
                 [], [], [], [], [], [], [], [], [], [], [], []]
MIN_LCM = 16000000
C = 100

sess = tf.Session()
env_tt = env(ACTION_DIM, ACTION_SPACE, OBSERVATION_DIM, TT_FRAMES, PATHS, MIN_LCM, C)

actor = A1C.Actor(sess, n_features=OBSERVATION_DIM, lr=LR_A, action_bound=ACTION_SPACE)
critic = A1C.Critic(sess, n_features=OBSERVATION_DIM, lr=LR_C)

sess.run(tf.global_variables_initializer())
ss = []
for i in range(2):
    s = env_tt.reset()
    t = 0
    s_temp = []
    ep_rs = []
    done = False
    # while done == False:
    while done == False:
        s_temp.append(s)
        a, mu, sigma = actor.choose_action(s)
        a_exp = np.exp(a)
        s_, r, done, a_eff = env_tt.step(a_exp)
        td_error = critic.learn(s, r, s_)
        actor.learn(s, a_eff, td_error)
        s = s_
        ep_rs.append(r)
        # print('a: ', a, '   mu:  ', mu, '   sigma:   ', sigma, '   a_eff:   ', a_eff, '  r:   ', r)
        if r == -500:
            print('循环截止次数：', j)
            break
    ss.append(s_temp)
    print('ep_rs_sum:   ', sum(ep_rs))

print(' ')
