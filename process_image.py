import time

import cv2
import numpy as np
import pytesseract
from skimage.metrics import structural_similarity as ssim


def save_image(img, counter):
    filename = "%d" % counter
    image_path = fr"resources/learning_screens/{filename}.png"
    cv2.imwrite(image_path, img)
    counter = counter + 1
    return counter


def get_gray_image(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img_gray

def get_thresh_image3(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    (T, threshInv) = cv2.threshold(blurred, 200, 255,
                                   cv2.THRESH_BINARY_INV)
    # cv2.imshow("Threshold Binary Inverse", threshInv)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    #
    # (T1, thresh) = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)
    # cv2.imshow("Threshold Binary", thresh)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    masked = cv2.bitwise_and(img, img, mask=threshInv)
    # cv2.imshow("Output", masked)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    print(gray.shape)
    return gray

def get_thresh_image2(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    (T, threshInv) = cv2.threshold(blurred, 200, 255,
                                   cv2.THRESH_BINARY_INV)
    cv2.imshow("Threshold Binary Inverse", threshInv)
    return threshInv


def get_thresh_image(img):
    img_gray = get_gray_image(img)
    ret, thresh = cv2.threshold(img_gray, 239, 255, cv2.THRESH_BINARY_INV)
    return thresh
    # return img_gray


def get_resized_image(img, counter):
    height, width, channels = img.shape
    img_resized = cv2.resize(img, (round(width // 6), round(height // 6)))
    # print('height', height, 'width', width, 'channels', channels)
    counter = save_image(img_resized, counter)
    return img_resized, counter


def get_screen(env):
    png = env.driver.get_screenshot_as_png()
    nparr = np.frombuffer(png, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img = cv2.resize(img, (1296, 710))
    return img


def compare_images(img1, img2):
    s = ssim(img1, img2)
    return s


def scroll_down(self):
    total_width = self.driver.execute_script("return document.body.offsetWidth")
    total_height = self.driver.execute_script("return document.body.parentNode.scrollHeight")
    viewport_width = self.driver.execute_script("return document.body.clientWidth")
    viewport_height = self.driver.execute_script("return window.innerHeight")

    rectangles = []

    i = 0
    while i < total_height:
        ii = 0
        top_height = i + viewport_height

        if top_height > total_height:
            top_height = total_height

        while ii < total_width:
            top_width = ii + viewport_width

            if top_width > total_width:
                top_width = total_width

            rectangles.append((ii, i, top_width, top_height))

            ii = ii + viewport_width

        i = i + viewport_height

    previous = None
    part = 0

    for rectangle in rectangles:
        if (not previous) is None:
            self.driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
            time.sleep(0.5)

        if rectangle[1] + viewport_height > total_height:
            offset = (rectangle[0], total_height - viewport_height)
        else:
            offset = (rectangle[0], rectangle[1])

        previous = rectangle

    return total_height, total_width
