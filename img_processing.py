# Code for image processing using openCV library
import matplotlib.pyplot as plt
from skimage import morphology
from scipy.ndimage.morphology import binary_fill_holes
import cv2

import numpy as np
import pandas as pd
import math


# Shows cvimage
def showImg(image):
    cv2.namedWindow("Img Preview", cv2.WINDOW_NORMAL)
    cv2.imshow("Img Preview", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    img = cv2.imread(r"data\4_1_4_BSE_001x250_cropped.jpg")

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    cv2.threshold(src=img, dst=img, thresh=5, maxval=255, type=cv2.THRESH_BINARY)
    cv2.imwrite(r'data/processed_images/binaryzation.png', img)
    dilated = cv2.dilate(img, (3, 3), iterations=1)
    cv2.imwrite(r'data/processed_images/dilated.png', dilated)
    eroded = cv2.erode(dilated, (3, 3), iterations=2)
    cv2.imwrite(r'data/processed_images/eroded.png', eroded)

    (cnt, hierarchy) = cv2.findContours(eroded.astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    f_img = np.ones((eroded.shape[0], eroded.shape[1]))
    f_img *= f_img * 255
    cv2.drawContours(f_img, cnt, -1, (0, 0, 255), 1)
    cv2.imwrite(r'data/processed_images/contours.png', f_img)
    # showImg(f_img)

    results = pd.DataFrame()
    count = 0
    circ_res = []
    round_res = []
    for idx in range(len(cnt)):
        if cv2.contourArea(cnt[idx]) > 0:
            c_area = cv2.contourArea(cnt[idx])
            c_perimeter = cv2.arcLength(cnt[idx], True)
            circularity = (4 * math.pi * c_area) / (c_perimeter ** 2)
            circ_res.append(circularity)
            if 0.1 < circularity < 0.9:
                M = cv2.moments(cnt[idx])
                count += 1
                cv2.putText(f_img, f"{count}",
                            [int(M['m10'] / M['m00']) + cv2.boundingRect(cnt[idx])[2], int(M['m01'] / M['m00'])],
                            cv2.FONT_HERSHEY_COMPLEX_SMALL, .5, [0, 0, 255], 1, cv2.LINE_AA)
                roundness = (4 * c_area) / (c_perimeter ** 2)
                round_res.append(roundness)
