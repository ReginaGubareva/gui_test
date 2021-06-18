import cv2
import numpy as np
import pytesseract
from skimage.metrics import structural_similarity as ssim


class ProcessImage:
    def __init__(self):
        pass

    def get_screen(self, env):
        png = env.driver.get_screenshot_as_png()
        nparr = np.frombuffer(png, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img = cv2.resize(img, (1296, 696))
        return img

    def get_resized_image(self, img, counter):
        height, width, channels = img.shape
        img_resized = cv2.resize(img, (round(width // 6), round(height // 6)))
        # print('height', height, 'width', width, 'channels', channels)
        counter = self.save_image(img_resized, counter)
        return img_resized, counter

    def get_gray_image(self, img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img_gray

    def get_thresh_image(self, img):
        img_gray = self.get_gray_image(img)
        ret, thresh = cv2.threshold(img_gray, 239, 255, cv2.THRESH_BINARY_INV)
        return thresh

    def save_image(self, img, counter):
        filename = "%d" % counter
        image_path = fr"D:\Projects\gui_test_model\resources\learning_screens\{filename}.png"
        cv2.imwrite(image_path, img)
        counter = counter + 1
        return counter

    @staticmethod
    def get_centroids(img):
        boxes = pytesseract.image_to_data(img)
        centroids = []
        for a, b in enumerate(boxes.splitlines()):
            centroid = []
            if a != 0:
                b = b.split()
                if len(b) == 12:
                    x, y, w, h = int(b[6]), int(b[7]), int(b[8]), int(b[9])
                    cv2.putText(img, b[11], (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 255), 2)
                    cv2.rectangle(img, (x, y), (x + w, y + h), (50, 50, 255), 2)
                    cv2.circle(img, (int(x + w / 2), int(y + h / 2)), 3, (255, 0, 0), 2)
                    centroid.append(int(x + w / 2))
                    centroid.append(int(y + h / 2))
                    centroids.append(centroid)

        return centroids

    @staticmethod
    def compare_images(img1, img2):
        s = ssim(img1, img2)
        return s
