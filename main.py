from environment import Environment
from ac_network import Agent
import utils

env = Environment()

agent = Agent(alpha=0.0003, gamma=0.99, n_actions=2)
score_history = []
score = 0
n_episodes = 20

for i in range(n_episodes):
    print('episode: ', i, 'score %.3f' % score)
    done = False
    score = 0
    counter = 0
    env.reset()
    # env.driver.execute_script("var myCanvas = document.createElement('canvas');" +
    #                           "document.body.appendChild(myCanvas);" +
    #                           "myCanvas.id = 'canvas';" +
    #                           "myCanvas.style.position = 'absolute';" +
    #                           "myCanvas.style.left = '0px';" +
    #                           "myCanvas.style.top = '0px';" +
    #                           "myCanvas.width = window.innerWidth;" +
    #                           "myCanvas.height = window.innerHeight;" +
    #
    #                           "var ctx = myCanvas.getContext('2d');" +
    #                           "myCanvas.addEventListener('click', function (event) {" +
    #                           "var x = event.clientX;" +
    #                           "var y = event.clientY;" +
    #                           "ctx.fillStyle = '#2980b9';" +
    #                           "ctx.beginPath();" +
    #                           "ctx.arc(x, y, 10, 0, 2 * Math.PI);" +
    #                           "ctx.fill();" +
    #                           "ctx.closePath();" +
    #                           "setTimeout(function () { ctx.clearRect(0, 0, myCanvas.width, myCanvas.height) }, 300);" +
    #                           "})")
    counter, centroids, state = env.get_observation(counter)
    # print('counter', counter, 'centroids', centroids, 'state', state)

    # while not done:
    for j in range(len(centroids)):
        action = agent.choose_action(state).numpy()
        # print("action", action)
        x = round(centroids[j][0] // 6)
        y = round(centroids[j][1] // 6)
        act = action[y][x]
        print('act:', act)
        state_, reward, done, info = env.step(act, centroids[j], counter)
        state = state_
        score += reward
    print('score: ', score)
    score_history.append(score)
    agent.learn()

filename = './resources/plot_learning/gui_test.png'
# plotLearning(score_history, filename=filename, window=25)