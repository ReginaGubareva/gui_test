import os
import random
import webbrowser
from io import BytesIO
import cv2
import time
import numpy as np
import pytesseract
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

import process_image as im_processor
import detect
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json


class Environment:
    def __init__(self):
        options = Options()
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('w3c', False)
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument('--disable-web-security')
        options.add_argument("--kiosk")
        prefs = {"credentials_enable_service": False,
                 "profile.password_manager_enabled": False}
        options.add_experimental_option("prefs", prefs)
        self.chrome = r"D:\chromedriver.exe"
        self.url = fr'https://vk.com/'
        self.driver = webdriver.Chrome(executable_path=self.chrome, chrome_options=options)
        self.driver.get(self.url)
        self.current_url = self.driver.current_url
        self.data = {}
        time.sleep(3)
        pytesseract.pytesseract.tesseract_cmd = fr"C:\Program Files\Tesseract-OCR\tesseract.exe"
        self.action_space = ['click', 'type']

    def reset(self):
        tabs_count = len(self.driver.window_handles)
        if tabs_count > 1:
            window = self.driver.current_window_handle
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.quit()
        elif self.url_changed():
            if self.driver.current_url == 'https://vk.com/feed':
                el = self.driver.find_element_by_id("top_logout_link")
                ac = ActionChains(self.driver)
                ac.move_to_element(el).click().perform()
                ac.reset_actions()
            else:
                self.driver.back()
            # self.driver.execute_script("window.open('');")
            # self.driver.switch_to.window(self.driver.window_handles[1])
            # self.driver.get("http://vk.com")
            # self.driver.switch_to.window(self.driver.window_handles[0])
            # self.driver.close()
        else:
            self.driver.refresh()
            time.sleep(1)

    def url_changed(self):
        if self.current_url == self.driver.current_url:
            return False
        else:
            return True

    def step(self, state, action, coordinates, counter):
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        done = False
        reward = 0
        counter = counter + 1

        ac = ActionChains(self.driver)
        body = self.driver.find_element_by_tag_name("body")
        value = ""
        random.shuffle(coordinates)
        for j in range(len(coordinates)):
            x = coordinates[j][0]
            y = coordinates[j][1]

            act = action[y][x]

            if act == 0:
                self.mark_element_click(x, y)
                self.act_click(x, y, ac, body)
                time.sleep(3)
                reward = self.close_new_window(reward)
                if self.is_terminal():
                    self.reset()
                    done = True
                    reward = 3
                    break
            if act == 1:
                value = self.get_value(x, y)
                if value is None:
                    value = ""
                self.mark_element_type(x, y)
                self.act_type(x, y, ac, body, value)
                time.sleep(3)
                reward = self.close_new_window(reward)
                if self.is_terminal():
                    self.reset()
                    done = True
                    reward = 3
                    break

        counter, centroids, state_ = self.get_observation(counter)

        return state_, reward, done, counter

    def get_value(self, x, y):
        for key in self.data:
            distance = abs(x - key[0]) + abs(y - key[1])
            if distance < 10:
                return self.data.get(key)
        return ""


    def act_click(self, x, y, ac, body):
        ac.move_to_element_with_offset(body, x, y).click().perform()
        ac.reset_actions()

    def act_type(self, x, y, ac, body, value):
        ac.move_to_element_with_offset(body, x, y).click().send_keys(value).perform()
        ac.reset_actions()

    def is_terminal(self):
        current_url = self.driver.current_url
        if current_url != self.url:
            self.url = current_url
            return True

    def no_changes(self, state):
        initial = cv2.imread("resources/initial.png")
        initial = cv2.resize(initial, (216, 116))
        initial = cv2.cvtColor(initial, cv2.COLOR_BGR2GRAY)

        state = cv2.resize(state, (216, 116))
        state = cv2.cvtColor(state, cv2.COLOR_BGR2GRAY)

        if im_processor.compare_images(initial, state) > 0.997:
            return True
        else:
            return False

    def get_observation(self, counter):
        img = im_processor.get_screen(self)
        if counter == 0:
            image_path = fr"D:\Projects\gui_test\resources\initial.png"
            cv2.imwrite(image_path, img)
        # img = im_processor.get_thresh_image3(img)
        # im_processor.save_image(img, counter)
        centroids = detect.centroid_detection(img, counter)
        # centroids = self.get_shift_centroids(centroids)
        counter += 1
        return counter, centroids, img

    def mark_centroids(self, x, y):
        self.driver.execute_script("let myCanvas = document.createElement('canvas');" +
                                   "document.body.appendChild(myCanvas);" +
                                   "myCanvas.id = 'canvas';" +
                                   "myCanvas.style.position = 'absolute';" +
                                   "myCanvas.style.left = '0px';" +
                                   "myCanvas.style.top = '0px';" +
                                   "myCanvas.width = window.innerWidth;" +
                                   "myCanvas.height = window.innerHeight;" +
                                   "let ctx = myCanvas.getContext('2d');" +
                                   "let x = " + str(x) + ";" +
                                   "let y = " + str(y) + ";" +
                                   "ctx.fillStyle = '#3b3131';" +
                                   "ctx.beginPath();" +
                                   "ctx.arc(x, y, 10, 0, 2 * Math.PI);" +
                                   "text = x + ' ' + y;" +
                                   "ctx.fillText(text, x+10, y+5);" +
                                   "ctx.fill();")

    def create_json_data(self, centroids):
        data = {self.url: []}
        for i in range(len(centroids)):
            element = self.driver.execute_script('return document.elementFromPoint(' +
                                                 str(centroids[i][0]) + ',' + str(centroids[i][1]) + ');')
            if element is not None:
                if element.tag_name == 'input':
                    # name = element.get_attribute("name")
                    # print("name: ", name, "centroids:", centroid, "data:", data)

                    text = self.driver.execute_script('el = document.elementFromPoint(' +
                                                      str(centroids[i][0]) + ',' + str(centroids[i][1]) + ');' +
                                                      'el.style.border="3px solid red";' +
                                                      'await new Promise(r => setTimeout(r, 3000));' +
                                                      'text = el.value;' +
                                                      'return text;')
                    data[self.url].append({
                        'name': element.get_attribute("name"),
                        'coordinates': str(centroids[i][0]) + ' ' + str(centroids[i][1]),
                        'text': text,
                        'tag name': element.tag_name
                    })
                    # print('text:', text)

                    with open('resources/hash_tables/hash_table.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)

    def mark_element_click(self, x, y):
        self.driver.execute_script('el = document.elementFromPoint(' + str(x) + ',' + str(y) + ');' +
                                   'el.style.border = "3px solid yellow";')

    def mark_element_type(self, x, y):
        self.driver.execute_script('el = document.elementFromPoint(' + str(x) + ',' + str(y) + ');' +
                                   'el.style.border = "3px solid purple";')

    def get_shift_centroids(self, centroids):
        centroids2 = []
        for centroid in centroids:
            buff = [centroid[0] - 3, centroid[1]]
            centroids2.append(buff)
        return centroids2

    def close_new_window(self, reward):
        reward += 1
        tabs_count = len(self.driver.window_handles)
        if tabs_count > 1:
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
        return reward

    def remove_repeated(self, centroids):
        result = list(dict.fromkeys(centroids))
        print(result)
        return result

# options.add_argument('--headless')
        # options.add_argument('--start-maximized')
        # options.set_capability('unhandledPromptBehavior', 'accept')
        # options.add_argument("--window-size=1296,710")

# f = open('resources/hash_tables/hash_table.json', )
# data = json.load(f)
# value = ""
# for i in data["https://vk.com/"]:
#     if i["coordinates"] == str(x) + " " + str(y):
#         print("in data, true")
#         if "input" == i["tag name"] or i["tag name"] == "text":
#             value = i["text"]


# f = open('resources/hash_tables/hash_table.json', )
        # data = json.load(f)
        # value = ""
        # for i in data["https://vk.com/"]:
        #     if i["coordinates"] == str(x) + " " + str(y):
        #         print("in data, true")
        #         if "input" == i["tag name"] or i["tag name"] == "text":
        #             value = i["text"]
        # return value

 # elements_the_same = True
                # self.driver.execute_script('el =  document.elementFromPoint(' + str(x) + ',' + str(y) +
                #                                            '); ' +
                #                                            'previous_el = document.elementFromPoint(' + str(previous_x)
                #                                            + ',' + str(previous_y) + '); ' +
                #                                            'const equal = el.isEqualNode(previous_el);'
                #                                            'return equal;')
            # if value == "":
            #     if elements_the_same:
            #         continue