from unityagents import UnityEnvironment
import numpy as np
from collections import deque
from tensorboardX import SummaryWriter
import os

from MADDPG import MADDPG

if __name__ == "__main__":
    env = UnityEnvironment(file_name="./Tennis_Linux/Tennis.x86_64", no_graphics=True)

    # get the default brain
    brain_name = env.brain_names[0]
    brain = env.brains[brain_name]

    # reset the environment
    env_info = env.reset(train_mode=True)[brain_name]

    # number of agents
    num_agents = len(env_info.agents)
    print('Number of agents:', num_agents)

    # size of each action
    action_size = brain.vector_action_space_size
    print('Size of each action:', action_size)

    # examine the state space
    states = env_info.vector_observations
    state_size = states.shape[1]
    print('There are {} agents. Each observes a state with length: {}'.format(states.shape[0], state_size))
    print('The state for the first agent looks like:', states[0])

    agents = MADDPG(state_size=24,
                    action_size=2,
                    n_agents=2,
                    gamma=0.99,
                    tau=1e-3,
                    lr_actor=1e-4,
                    lr_critic=5e-4,
                    learn_n_times_per_step=3,
                    update_target_every=10,
                    memory_size=int(1e5),
                    batch_size=256)

    agents.restore()  # load model

    n_episodes = 100
    max_t = 1000
    score_logger = []

    for i_episode in range(n_episodes):  # play game for 5 episodes
        env_info = env.reset(train_mode=True)[brain_name]  # reset the environment
        states = env_info.vector_observations  # get the current state (for each agent)
        scores = np.zeros(num_agents)  # initialize the score (for each agent)

        step_counter = 0
        while True:

            actions = agents.act(states)

            env_info = env.step(actions)[brain_name]  # send all actions to tne environment

            next_states = env_info.vector_observations  # get next state (for each agent)
            rewards = env_info.rewards  # get reward (for each agent)
            dones = env_info.local_done  # see if episode finished

            scores += env_info.rewards  # update the score (for each agent)
            states = next_states  # roll over states to next time step

            step_counter += 1
            if np.any(dones) or step_counter > max_t:  # exit loop if episode finished
                break

        score_logger.append(np.max(scores))
        print('episode: {}, max score: {}'.format(i_episode, np.max(scores)))

    env.close()

    print("avg score = ", np.mean(score_logger))

    import matplotlib.pyplot as plt
    plt.plot(np.arange(len(score_logger)), score_logger)
    plt.ylabel('score')
    plt.xlabel('episode')
    plt.show()
