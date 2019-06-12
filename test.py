#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#__author__ == 'GG_Adobe'

import cv2
import sys
import time
import base64
import logging
import numpy as np
import matplotlib.pyplot as plt

from time import sleep
from PIL import Image
from io import BytesIO
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

game_url = "chrome://dino"
chrome_driver_path = "F:/download/chromedriver_win32/chromedriver.exe"

#scripts
#create id for canvas for faster selection from DOM
init_script = "document.getElementsByClassName('runner-canvas')[0].id = 'runner-canvas'"

class Game:
    def __init__(self, custom_config=True):
        chrome_options = Options()
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_argument("--mute-audio")
        self._driver = webdriver.Chrome(
            executable_path=chrome_driver_path, chrome_options=chrome_options)
        self._driver.set_window_position(x=-10, y=0)
        self._driver.get(game_url)
        self._driver.execute_script("Runner.config.ACCELERATION=0")
        self._driver.execute_script(init_script)

    def get_crashed(self):
        return self._driver.execute_script("return Runner.instance_.crashed")

    def get_playing(self):
        return self._driver.execute_script("return Runner.instance_.playing")

    def restart(self):
        self._driver.execute_script("Runner.instance_.restart()")

    def press_up(self):
        self._driver.find_element_by_tag_name("body").send_keys(Keys.ARROW_UP)

    def get_score(self):
        score_array = self._driver.execute_script(
            "return Runner.instance_.distanceMeter.digits")
        # the javascript object is of type array with score in the formate[1,0,0] which is 100.
        score = ''.join(score_array)
        return int(score)

    def pause(self):
        return self._driver.execute_script("return Runner.instance_.stop()")

    def resume(self):
        return self._driver.execute_script("return Runner.instance_.play()")

    def end(self):
        self._driver.close()

def opration():
    dinoRun = Game()
    dinoRun.press_up()

    strategy1(dinoRun)

def judge_act(tmp, seed):
    di_sum = 0
    x1, y1, x2, y2 = 60, 70, 10, 16+seed
    for x in range(x1, y1):
        for y in range(x2,y2):
            di_sum += tmp[x][y]
    # print (len(tmp), tmp[25])
    if di_sum > 2000:
        return 1
    else:
        return 0

def show_img(img):
    # screen = (yield)
    # plt.ion()
    # plt.figure()
    plt.imshow(img)
    plt.axis("off") 
    # plt.ioff()
    plt.show()

def process_img(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # RGB to Grey Scale
    image = image[:300, :500]  # Crop Region of Interest(ROI)
    image = cv2.resize(image, (80, 80))
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image

def detect(_driver):
    getbase64Script = "canvasRunner = document.getElementById('runner-canvas'); return canvasRunner.toDataURL().substring(22)"
    image_b64 = _driver.execute_script(getbase64Script)
    screen = np.array(Image.open(BytesIO(base64.b64decode(image_b64))))
    image = process_img(screen)  # processing image as required
    return image


def strategy1(dinoRun):
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    plt.ion()
    speed = 0
    while True:
        # while dinoRun.get_crashed() == False:
        # dinoRun.press_up()
        img = detect(dinoRun._driver)

        # x1, y1, x2, y2 = 50, 50, 30, 50
        # lines = plt.plot(x1, y1, x2, y2)
        # use keyword args
        # plt.setp(lines, color='r', linewidth=2.0)
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # RGB to Grey Scale
        # plt.imshow(img)
        # plt.axis("off")
        # plt.show()
        # plt.pause(0.5)
        speed = dinoRun.get_score()//1000
        num = judge_act(img, speed)
        if num == 1:
            dinoRun.press_up()

        if dinoRun.get_crashed():
            score = dinoRun.get_score()
            logger.info('Score: {0}'.format(score))
            x = input()
            dinoRun.press_up()

    plt.ioff()
    plt.close()


if __name__ == "__main__":
    opration()
