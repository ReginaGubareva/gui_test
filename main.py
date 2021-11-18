from environment import Environment
from utils.plots import plotLearning
from ac_network import Agent

# from gym import wrappers

if __name__ == '__main__':
    env = Environment()
    agent = Agent(alpha=0.0003, gamma=0.99, n_actions=2)
    # env = gym.make('LunarLander-v2')
    # agent = PolicyGradientAgent(ALPHA=0.001, input_dims=[8], GAMMA=0.99, n_actions=4,
    #               layer1_size=128, layer2_size=128)

    score_history = []
    score = 0
    n_episodes = 30

    for i in range(n_episodes):
        print('episode: ', i, 'score %.3f' % score)
        done = False
        score = 0
        counter = 0
        reward = 0
        state_ = 0
        env.reset()
        counter, centroids, state = env.get_observation(counter)

        for j in range(len(centroids)):
            action = agent.choose_action(state).numpy()
            # print("action", action)
            x = round(centroids[j][0] // 6)
            y = round(centroids[j][1] // 6)
            act = action[y][x]
            print('act:', act)
            state_, reward, done, info = env.step(state, act, centroids[j], counter)
            state = state_
            score += reward
        score_history.append(score)
        agent.learn(state, reward, state_, done)

    filename = './resources/plot_learning/gui_test.png'
    plotLearning(score_history, filename=filename, window=25)
