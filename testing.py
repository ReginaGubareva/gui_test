import time
import numpy as np
import os
from selenium.webdriver.chrome import webdriver
from selenium.webdriver.chrome.options import Options
from torch.autograd import variable

from environment import Environment
from selenium.webdriver import ActionChains
import cv2
import pytesseract
from PIL import ImageGrab
from ac_network import Agent
from detect import centroid_detection
import json
from utils.plots import plotLearning
from selenium.webdriver.common.keys import Keys
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By


# import tensorflow as tf
# print(tf.__version__)
# print(tf.__path__)


# env = Environment()
# time.sleep(10)
# el = env.driver.find_element_by_id("top_profile_link")
# ac = ActionChains(env.driver)
# ac.move_to_element(el).click().perform()
# # el1 = env.driver.find_element_by_id("top_logout_link")
# # ac.move_to_element(el1).click().perform()
# # ac.reset_actions()
# env.driver.find_element_by_xpath("//select[@id='top_logout_link']/option[text()='Выйти']").click()

#############################################
############### True main  ##################
#############################################
env = Environment()
agent = Agent(alpha=0.0003, gamma=0.99, n_actions=2)

score_history = []
score = 0
n_episodes = 10
counter = 0

counter, centroids, state = env.get_observation(counter)

data = {}
for i in range(len(centroids)):

    element = env.driver.execute_script('return document.elementFromPoint(' +
                                        str(centroids[i][0]) + ',' + str(centroids[i][1]) + ');')
    if element is not None:
        if element.tag_name == 'input':
            text = env.driver.execute_script('el = document.elementFromPoint(' +
                                             str(centroids[i][0]) + ',' + str(centroids[i][1]) + ');' +
                                             'el.style.border="3px solid red";' +
                                             'await new Promise(r => setTimeout(r, 3000));' +
                                             'text = el.value;' +
                                             'return text;')
            data[centroids[i]] = text

# data = {(860, 504): '7', (437, 19): 'search', (960, 504): 'July',
#         (963, 151): '', (965, 105): '',
#         (960, 378): 'Ivan', (962, 423): 'Ivanov'}

env.data = data
env.reset()

f = open('weights/general_weights', "a")
average_episode_reward = 0
for i in range(n_episodes):

    f.write('episode: ' + str(i) + ' score: ' + str(score) + str("\n"))
    print('episode: ', i, ' score %.3f' % score)
    done = False
    score = 0
    reward = 0
    state_ = 0

    while not done:
        counter, centroids, state = env.get_observation(counter)
        action = agent.choose_action(state).numpy()
        state_, reward, done, counter = env.step(state, action, centroids, counter)

        if done:
            reward += 4

        if done and env.driver.current_url == 'https://vk.com/feed':
            reward += 5
            el = env.driver.find_element_by_id("top_logout_link")
            ac = ActionChains(env.driver)
            ac.move_to_element(el).click().perform()
            ac.reset_actions()

        state = state_
        score += reward
        agent.learn(state, reward, state_, done)
    average_episode_reward += score / counter
    score_history.append(average_episode_reward)
    f.write("\n")
f.close()
filename = './resources/plot_learning/gui_test.png'
plotLearning(score_history, filename=filename, window=25)


############################################
######## Get screen of full page  ##########
############################################
# env = Environment()
# counter = 2
# counter, centroids, state = env.get_observation(counter)
# for j in range(len(centroids)):
#     ac = ActionChains(env.driver)
#     element_body = env.driver.find_element_by_tag_name("body")
#     ac.move_to_element_with_offset(element_body, centroids[j][0], centroids[j][1]).click().perform()
#     time.sleep(2)
# env.driver.quit()


############################################
### Check if repeated elements exists  #####
############################################
# elements = []
# for i in range(len(centroids)):
#     el = env.driver.execute_script('el =  document.elementFromPoint(' +
#                                        str(centroids[i][0]) + ',' + str(centroids[i][1]) + ');' +
#                                        'return el;')
#     elements.append(el)
#
# print('el-s length', len(elements))
# for i in range(len(elements) - 1):
#     print('el_id', elements[i].get_attribute('name'))
#     if elements[i].id == elements[i+1].id:
#         print('repeated elements')


#############################################
########### Get web elements  ###############
#############################################
# env = Environment()
# counter = 0
# counter, centroids, state = env.get_observation(counter)
# data = {}
# data[env.url] = []
#
# centroids2 = []
# for centroid in centroids:
#     buff = [centroid[0] - 10, centroid[1]]
#     centroids2.append(buff)
#
# print('centroids', centroids)
# print('centroids2', centroids2)
#
# for i in range(len(centroids)):
#     element = env.driver.execute_script('return document.elementFromPoint(' +
#                                         str(centroids2[i][0]) + ',' + str(centroids2[i][1]) + ');')
#
#     if element.tag_name != "null" and (element.tag_name == "input" or
#        element.tag_name == "text"):
#
#         text = env.driver.execute_script('el = document.elementFromPoint(' +
#                                          str(centroids2[i][0]) + ',' + str(centroids2[i][1]) + ');' +
#                                          'el.style.border="3px solid red";' +
#                                          'await new Promise(r => setTimeout(r, 6000));' +
#                                          'text = el.value;' +
#                                          'return text;')
#         data[env.url].append({
#             'name': element.get_attribute("name"),
#             'coordinates': str(centroids2[i][0]) + ' ' + str(centroids2[i][1]),
#             'text': text,
#             'tag name': element.tag_name
#         })
#         print('text:', text)
#
#     with open('resources/hash_tables/hash_table1.json', 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=4)

# {"https://vk.com/": [{"name": "email", "centroids": "967 105", "data": ""},
# {"name": "pass", "centroids": "966 152", "data": ""}]}
# {
#             "name": "",
#             "coordinates": "1061 504",
#             "text": "1995",
#             "tag name": "input"
#         }


#############################################
############### Test main  ##################
#############################################
# env = Environment()
# agent = Agent(alpha=0.0003, gamma=0.99, n_actions=2)
#
# score_history = []
# score = 0
# n_episodes = 10
# counter, centroids, state = env.get_observation(0)
#
# centroids2 = []
# for centroid in centroids:
#     buff = [centroid[0] - 10, centroid[1]]
#     centroids2.append(buff)
#
# # for i in range(n_episodes):
# #     env.create_json_data(centroids2)
#
# f = open('weights/general_weights', "a")
# for i in range(n_episodes):
#     f.write('episode: ' + str(i) + ' score: ' + str(score) + str("\n"))
#     print('episode: ', i, ' score %.3f' % score)
#     done = False
#     score = 0
#     counter = 0
#     reward = 0
#     state_ = 0
#     env.reset()
#     counter, centroids, state = env.get_observation(counter)
#     centroids2 = []
#     for centroid in centroids:
#         buff = [centroid[0] - 10, centroid[1]]
#         centroids2.append(buff)
#
#     for j in range(len(centroids2)):
#         action = agent.choose_action(state).numpy()
#         # print("action", action)
#         x = round(centroids2[j][0] // 6)
#         y = round(centroids2[j][1] // 6)
#         act = action[y][x]
#
#         state_, reward, done, info = env.step(state, act, centroids2[j], counter)
#         f.write("   action: " + str(act) + " x: " + str(x) + " y: " + str(y) + " reward: " + str(reward) + "\n")
#         state = state_
#         score += reward
#         score_history.append(score)
#         agent.learn(state, reward, state_, done)
#     f.write("\n")
# f.close()
# filename = './resources/plot_learning/gui_test.png'
# plotLearning(score_history, filename=filename, window=25)


#############################################
############### Test json  ##################
#############################################
# env = Environment()
#
# counter = 0
# counter, centroids, state = env.get_observation(counter)
# f = open('resources/hash_tables/hash_table.json', )
# data = json.load(f)
# value = ""
#
#
# ac = ActionChains(env.driver)
# element_body = env.driver.find_element_by_tag_name("body")
#
# for i in data["https://vk.com/"]:
#     # print("i[centroids]:", i["centroids"])
#     for j in range(len(centroids)):
#         # env.mark_centroids(str(centroids[j][0]), str(centroids[j][1]))
#
#         if i["centroids"] == str(centroids[j][0]) + " " + str(centroids[j][0]):
#             print("True")
#         value = i["data"]
#     print("value", value)
#     ac.move_to_element_with_offset(element_body, centroids[j][0], centroids[j][1]) \
#         .click().send_keys(value).perform()
#     time.sleep(2)


#############################################
############# Compare images ################
#############################################
# env = Environment()
# counter = 0
# state = cv2.imread("resources/initial.png")
# state = cv2.resize(state, (216, 116))
# state = cv2.cvtColor(state, cv2.COLOR_BGR2GRAY)
#
# print('state:', state.shape)
# for i in range(3):
#     print('counter', counter)
#     counter, observation, screen = env.get_observation(counter)
#     state1 = cv2.resize(screen, (216, 116))
#     state1 = cv2.cvtColor(state1, cv2.COLOR_BGR2GRAY)
#     print('state1:', state1.shape)
#
#     if env.image_processor.compare_images(state1, state) > 0.997:
#         state = state1
#         print(True)
#     else:
#         state = state1
#         print(False)

#############################################
## Check centroids for thresh and for img  ##
#############################################
# env = Environment()
# img = env.image_processor.get_screen(env)
# thresh = env.image_processor.get_gray_image(img)
# centroids_img = centroid_detection(img, counter=0)
# centroids_thresh = centroid_detection(thresh, counter=0)
# for j in range(len(centroids_img)):
#     env.driver.execute_script("let myCanvas = document.createElement('canvas');" +
#                               "document.body.appendChild(myCanvas);" +
#                               "myCanvas.id = 'canvas';" +
#                               "myCanvas.style.position = 'absolute';" +
#                               "myCanvas.style.left = '0px';" +
#                               "myCanvas.style.top = '0px';" +
#                               "myCanvas.width = window.innerWidth;" +
#                               "myCanvas.height = window.innerHeight;" +
#                               "let ctx = myCanvas.getContext('2d');" +
#                               "let x = " + str(centroids_img[j][0]) + ";" +
#                               "let y = " + str(centroids_img[j][1]) + ";" +
#                               "ctx.fillStyle = '#fef907';" +
#                               "ctx.beginPath();" +
#                               "ctx.arc(x, y, 10, 0, 2 * Math.PI);" +
#                               "ctx.fill();")

# for j in range(len(centroids_thresh)):
#     env.driver.execute_script("let myCanvas = document.createElement('canvas');" +
#                               "document.body.appendChild(myCanvas);" +
#                               "myCanvas.id = 'canvas';" +
#                               "myCanvas.style.position = 'absolute';" +
#                               "myCanvas.style.left = '0px';" +
#                               "myCanvas.style.top = '0px';" +
#                               "myCanvas.width = window.innerWidth;" +
#                               "myCanvas.height = window.innerHeight;" +
#                               "let ctx = myCanvas.getContext('2d');" +
#                               "let x = " + str(centroids_thresh[j][0]) + ";" +
#                               "let y = " + str(centroids_thresh[j][1]) + ";" +
#                               "ctx.fillStyle = '#ff3333';" +
#                               "ctx.beginPath();" +
#                               "ctx.arc(x, y, 10, 0, 2 * Math.PI);" +
#                               "ctx.fill();")


#############################################
############ Mark centroids  ################
#############################################
# env.driver.execute_script("let myCanvas = document.createElement('canvas');" +
#                           "document.body.appendChild(myCanvas);" +
#                           "myCanvas.id = 'canvas';" +
#                           "myCanvas.style.position = 'absolute';" +
#                           "myCanvas.style.left = '0px';" +
#                           "myCanvas.style.top = '0px';" +
#                           "myCanvas.width = window.innerWidth;" +
#                           "myCanvas.height = window.innerHeight;" +
#                           "let ctx = myCanvas.getContext('2d');" +
#                           "let x = " + str(centroids[j][0]) + ";" +
#                           "let y = " + str(centroids[j][1]) + ";" +
#                           "ctx.fillStyle = '#2980b9';" +
#                           "ctx.beginPath();" +
#                           "ctx.arc(x, y, 10, 0, 2 * Math.PI);" +
#                           "ctx.fill();")

#############################################
########### Get coordinates  ################
#############################################
# env.driver.execute_script("function printMousePos(event) {" +
#                           "document.body.textContent =" +
#                           "'clientX: ' + event.clientX +" +
#                           " '- clientY: ' + event.clientY; " +
#                           "}" +
#                           "document.addEventListener('click', printMousePos);")

#############################################
########### Working typing  #################
#############################################
# ac = ActionChains(env.driver)
# element_body = env.driver.find_element_by_tag_name("body")
# ac.move_to_element_with_offset(element_body, 948, 109)
# ac.click().send_keys('login').perform()

#############################################
########### Test write in json  #############
#############################################
# env = Environment()
#
# url = env.driver.current_url
# data = {url: []}
# counter = 2
# counter, centroids, state = env.get_observation(counter)
# print(centroids)
#
#
# inputs = env.driver.execute_script("return document.getElementsByTagName('input');")
# for i in range(len(centroids)):
#     clas = inputs[i].get_attribute("class")
#     print(inputs[i].get_attribute("name"), str(centroids[i][0]) + " " + str(centroids[i][1]))
#     if "input" in clas:
#         data[url].append({
#             'name': inputs[i].get_attribute("name"),
#             'centroids': str(centroids[i][0]) + " " + str(centroids[i][1]),
#             'data': ''
#         })
#
# with open('resources/hash_tables/hash_table.json', 'w') as outfile:
#     json.dump(data, outfile)


#############################################
############# Test hash tables  #############
#############################################
# url, name, centroids, data

# env = Environment()
# counter = 2
# counter, centroids, state = env.get_observation(counter)
# print(centroids)
#
#
# inputs = env.driver.execute_script("return document.getElementsByTagName('input');")
# for i in range(len(inputs)):
#     clas = inputs[i].get_attribute("class")
#     if "input" in clas:
#         print('input name', i, ':', type(clas))
#         env.driver.execute_script("let myCanvas = document.createElement('canvas');" +
#                                   "document.body.appendChild(myCanvas);" +
#                                   "myCanvas.id = 'canvas';" +
#                                   "myCanvas.style.position = 'absolute';" +
#                                   "myCanvas.style.left = '0px';" +
#                                   "myCanvas.style.top = '0px';" +
#                                   "myCanvas.width = window.innerWidth;" +
#                                   "myCanvas.height = window.innerHeight;" +
#                                   "let ctx = myCanvas.getContext('2d');" +
#                                   "let x = " + str(centroids[i][0]) + ";" +
#                                   "let y = " + str(centroids[i][1]) + ";" +
#                                   "ctx.fillStyle = '#2980b9';" +
#                                   "ctx.beginPath();" +
#                                   "ctx.arc(x, y, 10, 0, 2 * Math.PI);" +
#                                   "ctx.fill();")


# for i in range(len(centroids)):
#     env.driver.execute_script("element = document.elementFromPoint(arguments[0],arguments[1]); " +
#                               "if(element != null){" +
#                               "if (element.tagName && element.tagName.toLowerCase() == 'textarea' " +
#                               "|| element.tagName && element.tagName.toLowerCase() == 'inputtype') { " +
#                               "console.log('this is a textarea');" +
#                               "}" +
#                               "}"
#                               , centroids[i][0], centroids[i][1])
# print(element)
# if element is not None:
#     env.driver.execute_script("elem.style.color = red;")

# element = env.driver.find_element_by_css_selector("input[type='submit']")
# print('element:', element.text)

#############################################
####### Get centroids with opencv  ##########
#############################################
# @staticmethod
# def get_centroids(img):
#     boxes = pytesseract.image_to_data(img)
#     centroids = []
#     for a, b in enumerate(boxes.splitlines()):
#         centroid = []
#         if a != 0:
#             b = b.split()
#             if len(b) == 12:
#                 x, y, w, h = int(b[6]), int(b[7]), int(b[8]), int(b[9])
#                 cv2.putText(img, b[11], (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 255), 2)
#                 cv2.rectangle(img, (x, y), (x + w, y + h), (50, 50, 255), 2)
#                 cv2.circle(img, (int(x + w / 2), int(y + h / 2)), 3, (255, 0, 0), 2)
#                 centroid.append(int(x + w / 2))
#                 centroid.append(int(y + h / 2))
#                 centroids.append(centroid)
#
#     return centroids


#############################################
############# Test centroids  ###############
#############################################
# env = Environment()
#
# agent = Agent(alpha=0.0003, gamma=0.99, n_actions=2)
# score_history = []
# score = 0
# n_episodes = 20
# counter = 0
#
# counter, centroids, state = env.get_observation(counter)
#
# for j in range(len(centroids)):
#     env.driver.execute_script("let myCanvas = document.createElement('canvas');" +
#                               "document.body.appendChild(myCanvas);" +
#                               "myCanvas.id = 'canvas';" +
#                               "myCanvas.style.position = 'absolute';" +
#                               "myCanvas.style.left = '0px';" +
#                               "myCanvas.style.top = '0px';" +
#                               "myCanvas.width = window.innerWidth;" +
#                               "myCanvas.height = window.innerHeight;" +
#                               "let ctx = myCanvas.getContext('2d');" +
#                               "let x = " + str(centroids[j][0]) + ";" +
#                               "let y = " + str(centroids[j][1]) + ";" +
#                               "ctx.fillStyle = '#2980b9';" +
#                               "ctx.beginPath();" +
#                               "ctx.arc(x, y, 10, 0, 2 * Math.PI);" +
#                               "ctx.fill();")


#############################################
############### Test detection  #############
#############################################
# img = cv2.imread("resources/test_images/initial.jpg")
# img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#
# centroids = centroid_detection(img)

# env = Environment()
#
# img = cv2.imread(fr"resources/test_images/initial.jpg")
# counter = 0
#
# counter, centroids, state, screen = env.get_observation(counter)
# for i in range(len(centroids)):
#     cv2.circle(screen, centroids[i], 5, (0, 0, 255), thickness=3, lineType=cv2.LINE_AA)
#
#
# cv2.imshow('Contours', screen)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


#############################################
############### Test main   #################
#############################################
# env = Environment()
#
# agent = Agent(alpha=0.0003, gamma=0.99, n_actions=2)
# score_history = []
# score = 0
# n_episodes = 20
# counter = 0
#
# counter, centroids, state = env.get_observation(counter)
# for i in range(n_episodes):
#     print('episode: ', i, 'score %.3f' % score)
#     done = False
#     score = 0
#     counter = 0
#     env.reset()
#
#     counter, centroids, state = env.get_observation(counter)
#     print('counter', counter, 'centroids', centroids, 'state', state)
#     env.driver.execute_script("var myCanvas = document.createElement('canvas');" +
#                               "document.body.appendChild(myCanvas);" +
#                               "myCanvas.id = 'canvas';" +
#                               "myCanvas.style.position = 'absolute';" +
#                               "myCanvas.style.left = '0px';" +
#                               "myCanvas.style.top = '0px';" +
#                               "myCanvas.width = window.innerWidth;" +
#                               "myCanvas.height = window.innerHeight;" +
#
#                               "var ctx = myCanvas.getContext('2d');" +
#                               "myCanvas.addEventListener('click', function (event) {" +
#                               "var x = event.clientX;" +
#                               "var y = event.clientY;" +
#                               "ctx.fillStyle = '#2980b9';" +
#                               "ctx.beginPath();" +
#                               "ctx.arc(x, y, 10, 0, 2 * Math.PI);" +
#                               "ctx.fill();" +
#                               "ctx.closePath();" +
#                               "setTimeout(function () { ctx.clearRect(0, 0, myCanvas.width, myCanvas.height) }, 300);" +
#                               "})")
#
#     for j in range(len(centroids)):
#         action = agent.choose_action(state).numpy()
#         # print("action", action)
#         x = round(centroids[j][0] // 6)
#         y = round(centroids[j][1] // 6)
#         act = action[y][x]
#         print('act:', act)
#         state_, reward, done, info = env.step(act, centroids[j], counter)
#         state = state_
#         score += reward
#     print('score: ', score)
#     score_history.append(score)
#     agent.learn()

# filename = './resources/plot_learning/gui_test.png'
# plotLearning(score_history, filename=filename, window=25)


#############################################
######### Test type with selenium ###########
#############################################
# env = Environment()
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
# print(env.driver.get_window_size('current'))
# counter = 0
# number_of_episodes = 20
# counter, centroids, state = env.get_observation(counter)
# print(centroids)
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# ac = ActionChains(env.driver)
# element_body = env.driver.find_element_by_tag_name("body")
# print("body coordinates: ", element_body.location)
# ac.move_to_element(element_body)
# for i in range(len(centroids)):
#
#     print(i, '-', centroids[i][0], centroids[i][1])
#     element = env.driver.execute_script("return document.elementFromPoint(" + str(centroids[i][0]) + ", "
#                                         + str(centroids[i][1]) + ");")
#
#     if element is not None:
#         ac.move_to_element_with_offset(element_body, centroids[i][0], centroids[i][1]).click().perform()
#         time.sleep(1)
#         ac.move_to_element(element).send_keys('')
#         print(element)


#############################################
############## Test get action ##############
#############################################
# env = Environment()
# counter = 0
# counter, centroids, state = env.get_observation(counter)
# print('centroids:', centroids)
# agent = Agent(alpha=0.0003, gamma=0.99, n_actions=2)
# action = agent.choose_action(state).numpy()
# print('action:', action)
# for j in range(len(centroids)):
#     x = round(centroids[j][0] // 6)
#     y = round(centroids[j][1] // 6)
#     act = action[y][x]
#     print('x:', x, 'y:', y, 'act:', act)


#############################################
########### Test get_observation ############
#############################################
# env = Environment()
# counter = 0
# while counter < 5:
#     counter, centroids, state = env.get_observation(counter)
#     print(centroids)


#############################################
######## Test model ac_tensorflow  ##########
#############################################
# env = Environment()
# score_history = []
# score = 0
# n_episodes = 100
#
# for i in range(n_episodes):
#     counter = 0
#     j = 0
#     counter, centroids, state = env.get_observation(counter)
#     print('centroids:', centroids)
#     print('state shape: ', state.shape)
#     done = False
#     agent = Agent(alpha=0.0003, gamma=0.99, n_actions=2)
#     action = agent.choose_action(state).numpy()
#     print('action shape:', action.shape)
#     print('number of centroids:', len(centroids))
#     if i != 0:
#         env.reset()
#     while not done:
#         while j < len(centroids):
#             print('done:', done)
#             # for j in range(len(centroids)):
#             print('Episode number #', j)
#             x = round(centroids[j][0] // 6)
#             y = round(centroids[j][1] // 6)
#             act = action[y][x]
#             print('x: ', x, 'y: ', y, 'act: ', act)
#             state_, reward, done, counter = env.step(act, centroids[j], counter)
#             j += 1

#############################################
######## Create file with elements ##########
#############################################
# var canv = document.createElement('canvas');
# canv.id = 'canvas';
# document.body.appendChild(canv);
# var ctx = canv.getContext('2d');
# canv.addEventListener("click",function(event) {
#   var x = event.clientX;
#   var y = event.clientY;
#   var radius = 5;
#   ctx.beginPath();
#   ctx.arc(x, y, radius, 40, 0, 2 * Math.PI);
#   ctx.stroke();
#   var coords = 'X coords: ' + x + ', Y coords: ' + y;
#   console.log(coords);
# })


#
# var canv = document.createElement('canvas');
# canv.id = 'canvas';
# document.body.appendChild(canv);
# var ctx = canv.getContext('2d');
# canv.addEventListener("click",function(event) {
#   var x = event.clientX;
#   var y = event.clientY;
#   var radius = 5;
#   ctx.beginPath();
#   ctx.arc(x, y, radius, 40, 0, 2 * Math.PI);
#   ctx.fill();
#   ctx.fillStyle = 'red';
#   var coords = 'X coords: ' + x + ', Y coords: ' + y;
#   console.log(coords);
# })


#############################################
########## Try to use Selenium ##############
#############################################
# env = Environment()
# print(env.driver.get_window_size('current'))
# counter = 0
# counter, centroids, state = env.get_observation(counter)
# print(centroids)
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# ac = ActionChains(env.driver)
# element_body = env.driver.find_element_by_tag_name("body")
# print("body coordinates: ", element_body.location)
# ac.move_to_element(element_body)
# for i in range(len(centroids)):
#     print(i, '-', centroids[i][0], centroids[i][1])
#     ac.move_to_element_with_offset(element_body, centroids[i][0], centroids[i][1]).click().perform()
#     time.sleep(3)


#############################################
########## Check if new tab opened ##########
#############################################
# env = Environment()
# time.sleep(5)
# tabs_count = len(env.driver.window_handles)
# if tabs_count > 1:
#     env.driver.switch_to.window(env.driver.window_handles[1])
#     env.driver.close()


#############################################
##### is_terminal function selenium  ########
#############################################
# env = Environment()
# initial_url = fr'http://localhost/customer/login'
# current_url = env.driver.current_url
# if current_url == initial_url:
#     print(False)
# else:
#     initial_url = current_url
#     print(True)


#############################################
##### is_terminal function pyautogui  ########
#############################################
# pyautogui.click(0, 200)  # a random click for focusing the browser
# pyautogui.press('f6')
# pyautogui.hotkey('ctrl', 'c')
# url = pyperclip.paste()
# print(url)
# if url == self.url:
#     return False
# else:
#     self.url = url
#     return True


#############################################
############   Reset function   #############
#############################################
# env = Environment()
# time.sleep(12)
# env.reset()


#############################################
#### Test model pytorch with the image ######
#############################################
# env = Environment()
# counter = 0
# counter, observation, img_resized = env.get_env_observation(counter)
# print(observation)
# agent = PolicyGradientAgent(ALPHA=0.001, input_dims=[len(observation)],
#                             output_dims=[len(observation)],
#                             GAMMA=0.99, n_actions=2,
#                             layer1_size=128, layer2_size=128)


#############################################
##########  Test model pytorch  #############
#############################################
# env = Environment()
# counter = 0
# counter, observation, img_resized = env.get_env_observation(counter)
# print(observation)
# agent = PolicyGradientAgent(ALPHA=0.001, input_dims=[len(observation)], output_dims=[len(observation)],
#                             GAMMA=0.99, n_actions=2,
#                             layer1_size=128, layer2_size=128)
# action = agent.choose_action(observation)
# print('action item', action)


#############################################
##### Test get tensor for centroids #########
#############################################
# counter = 8
# env = Environment()
# counter, img, thresh = env.get_screen(counter)
# centroids = env.get_centroids(thresh)
# observation = []
# height, width = img.shape
# normal_array = img/255
# print(len(centroids))
# for k in centroids:
#     y = k[0]
#     x = k[1]
#     observation.append(normal_array[x][y])
# print(observation)
# counter, observation = env.get_env_observation(counter)
# print(observation)


############################################
######## Check gym observation  ############
############################################
# env2 = gym.make('LunarLander-v2')
# observation = env2.reset()
# print('observation', observation)


############################################
######### Check environment  ###############
############################################
# env = Environment()
# counter = 2
# counter, img, thresh = env.get_screen(counter)
# filename = "%d" % counter
# image_path = fr"D:\projects\sber-gui-test-pytorch\resources\learning_screens\{filename}.png"
# cv2.imwrite(image_path, thresh)


############################################
#########    Check SSIM      ###############
############################################
# img1 = cv2.imread(fr"D:\projects\sber-gui-test-pytorch\resources\learning_screens\initial1.png")
# img2 = cv2.imread(fr"D:\projects\sber-gui-test-pytorch\resources\learning_screens\thresh.png")
# im_gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
# im_gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
# print(env.compare_images(im_gray1, im_gray2))


############################################
######### Draw all countours  ##############
############################################
# centroids = env.get_centroids(thresh)
# print('cenroids:', centroids)
# print("Number of Centroids found = " + str(len(centroids)))
#
# # for i in range(len(contours)):
# #     cnt = contours[i]
# #     cv2.drawContours(img, [cnt], 0, (0, 0, 255), 2)
# #
# # cv2.imshow('Contours', img)
# # cv2.waitKey(0)
# # cv2.destroyAllWindows()
#
# for i in range(len(centroids)):
#     cX = centroids[i][0]
#     cY = centroids[i][1]
#     cv2.circle(img, (cX, cY), 5, (0, 255, 0), 1)
#
# cv2.imshow('Centroids', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


#############################################
########## Text recognition OCR   ###########
#############################################
# pytesseract.pytesseract.tesseract_cmd = fr"C:\Users\u13250\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
# image_path = fr"D:\projects\sber-gui-test-pytorch\resources\learning_screens\4.png"
# img = cv2.imread(image_path)

#############################################
########## Detecting Characters  ############
#############################################
# hImg, wImg, _ = img.shape
# boxes = pytesseract.image_to_boxes(img)
# for b in boxes.splitlines():
#     print(b)
#     b = b.split(' ')
#     print(b)
#     x, y, w, h = int(b[1]), int(b[2]), int(b[3]), int(b[4])
#     cv2.rectangle(img, (x, hImg - y), (w, hImg - h), (50, 50, 255), 2)
#     cv2.putText(img, b[0], (x, hImg - y + 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 255), 2)
#
# cv2.imshow('img', img)
# cv2.waitKey(0)

#############################################
########## Detecting Words  ############
############################################
# boxes = pytesseract.image_to_data(img)
# # print('boxes:', boxes)
# centroids = []
# for a, b in enumerate(boxes.splitlines()):
#     centroid = []
#     # print('a: ', a, 'b: ', b)
#     if a != 0:
#         b = b.split()
#         if len(b) == 12:
#             x, y, w, h = int(b[6]), int(b[7]), int(b[8]), int(b[9])
#             # print('x:', x, 'y:', y)
#             cv2.putText(img, b[11], (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 255), 2)
#             cv2.rectangle(img, (x, y), (x + w, y + h), (50, 50, 255), 2)
#             cv2.circle(img, (int(x + w/2), int(y + h/2)), 3, (255, 0, 0), 2)
#             centroid.append(int(x + w/2))
#             centroid.append(int(y + h/2))
#             centroids.append(centroid)
# print(centroids)
# cv2.imshow('img', img)
# cv2.waitKey(0)


#############################################
##########       Flood Fill       ###########
#############################################
# image_path = fr"D:\projects\sber-gui-test-pytorch\resources\learning_screens\initial1.png"
# flood = cv2.imread(image_path)
# seed = (180, 80)
# cv2.floodFill(flood, None, seedPoint=seed, newVal=(0, 0, 255), loDiff=(5, 5, 5, 5), upDiff=(5, 5, 5, 5))
# cv2.circle(flood, seed, 2, (0, 255, 0), cv2.FILLED, cv2.LINE_AA);
# cv2.imshow('flood', flood)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


#############################################
########## Convert image to array ###########
#############################################
# data = np.asarray(img, dtype="int32")
# print('data:', data)

#############################################
###### Get centroid of ui component  ########
#############################################
# contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# print("Number of Contours found = " + str(len(contours)))
# centroids = []
# for i in range(len(contours)):
#     if len(contours[i]) < 4:
#         continue
#     Cx = 0
#     Cy = 0
#     for j in range(len(contours[i])):
#         Cx += contours[i][j][0][0]
#         Cy += contours[i][j][0][1]
#
#     Cx = int(Cx / len(contours[i]))
#     Cy = int(Cy / len(contours[i]))
#     C = [Cx, Cy]
#     centroids.append(C)
# print(centroids)
# return centroids

#############################################
########### Get screen pyautogui  ###########
#############################################
# def get_screen_pyautogui(self, counter):
#     filename = "%d" % counter
#     pyautogui.hotkey('f11')
#     time.sleep(5)
#     png = pyautogui.screenshot()
#     img = cv2.cvtColor(np.array(png), cv2.COLOR_RGB2BGR)
#     print(type(img))
#     image_path = fr"D:\projects\sber-gui-test-pytorch\resources\learning_screens\{filename}.png"
#     im_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     ret, thresh = cv2.threshold(im_gray, 239, 255, cv2.THRESH_BINARY_INV)
#     cv2.imwrite(image_path, img)
#     counter += 1
#     return counter, img, thresh
