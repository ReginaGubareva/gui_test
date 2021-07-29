import os
import webbrowser
from io import BytesIO
import cv2
import time
import numpy as np
import pytesseract
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from process_image import ProcessImage
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
        # options.add_argument("--window-size=1296,710")
        options.add_argument("--kiosk")
        self.chrome = r"D:\chromedriver.exe"
        self.url = fr'https://vk.com/'
        self.driver = webdriver.Chrome(executable_path=self.chrome, chrome_options=options)
        self.driver.get(self.url)
        self.image_processor = ProcessImage()
        time.sleep(3)
        pytesseract.pytesseract.tesseract_cmd = fr"C:\Program Files\Tesseract-OCR\tesseract.exe"
        self.action_space = ['click', 'type']

    def reset(self):
        tabs_count = len(self.driver.window_handles)
        if tabs_count > 1:
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.close()
        else:
            # self.driver.back()
            self.driver.refresh()
            time.sleep(1)

    def step(self, action, coordinates, counter):
        done = False
        reward = 0
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        ac = ActionChains(self.driver)
        element_body = self.driver.find_element_by_tag_name("body")
        if action == 0:
            ac.move_to_element_with_offset(element_body, coordinates[0], coordinates[1]).click().perform()
            time.sleep(2)
            counter, centroids, state_ = self.get_observation(counter)
            if self.is_terminal(self):
                done = True
                reward = 3
                # print("Done")
            if self.no_changes(state_):
                reward = -1
                # print('No changes')
        if action == 1:
            # f = open('resources/hash_tables/hash_table.json', )
            # data = json.load(f)
            # value = ""
            # for i in data["https://vk.com/"]:
            #     if i["centroids"] == str(coordinates[0]) + " " + str(coordinates[1]):
            #         value = i["data"]
            # print("value: ", value)
            # if value != "":
            ac.move_to_element_with_offset(element_body, coordinates[0], coordinates[1])\
                        .click().perform()
            ac.send_keys("blabla")

            time.sleep(2)

            counter, centroids, state_ = self.get_observation(counter)
            if self.is_terminal(self):
                reward = 3
                done = True
                # print("Done")
            if self.no_changes(state_):
                reward = -1
                # print('No changes')
        return state_, reward, done, counter

    @staticmethod
    def is_terminal(self):
        current_url = self.driver.current_url
        if current_url != self.url:
            self.url = current_url
            return True

    def no_changes(self, state):
        initial = cv2.imread("resources/initial.jpg")
        # initial = cv2.resize(initial, (216, 116))
        initial = cv2.cvtColor(initial, cv2.COLOR_BGR2GRAY)
        # print('shapes:', initial.shape, state.shape)
        state = cv2.cvtColor(state, cv2.COLOR_BGR2GRAY)
        if self.image_processor.compare_images(state, initial) > 0.997:
            state2 = state
            return True
        else:
            state2 = state
            return False

    def get_observation(self, counter):
        img = self.image_processor.get_screen(self)
        thresh = self.image_processor.get_thresh_image(img)
        # state, counter = self.image_processor.get_resized_image(img, counter)
        centroids = detect.centroid_detection(img, counter)
        return counter, centroids, img



