import cv2
import numpy as np
import datetime


def shadow_remove(image):
    rgb_planes = cv2.split(image)
    result_norm_planes = []
    for plane in rgb_planes:
        dilated_img = cv2.dilate(plane, np.ones((7, 7), np.uint8))
        bg_img = cv2.medianBlur(dilated_img, 21)
        diff_img = 255 - cv2.absdiff(plane, bg_img)
        norm_img = cv2.normalize(diff_img, None, alpha=0, beta=180, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
        result_norm_planes.append(norm_img)

    return cv2.merge(result_norm_planes)

# Return numpy.array of polynomial fit values for X range of image width
def row_polynom_vals(image, row, polynom_degree):
    return np.polyval(p=np.polyfit(x=range(image.shape[1]), y=image[row], deg=polynom_degree),
                      x=range(0, image.shape[1]))


# Changing numpy.array values into np.array of shadowing intensity (regarding 1st el. of array)
# For purposes of calculating ShI (Shadow Intensity)
def ShI_arr(values):
    for idx in range(1, values.size):
        values[idx] = 1 - values[idx] / values[0]
    return values


# Function for proper addition of two pixel intensities
# By default, adding pixels intensity can end up in changing the white pixel into black (from 255 to 0)
# i.e. 240 + 20 = 5 (not 260 nor 255)
def pxl_intensity_add(intens1, intens2):
    if float(intens1) + float(intens2) > 255:
        return 255
    else:
        return float(intens1) + float(intens2)


def pxl_intensity_subtract(intens1, intens2):
    if intens1 - intens2 > 0:
        return 0
    else:
        return intens1 - intens2


def pxl_intensity_multiply(intens1, coef):
    if intens1 * coef > 255:
        return 255
    else:
        return intens1 * coef


def normalize_img_line(image_line, fitted_polynomial):
    for pxl_pos in range(len(image_line)):
        if image_line[pxl_pos] < fitted_polynomial[pxl_pos]:
            image_line[pxl_pos] = pxl_intensity_multiply(image_line[pxl_pos], (1 + ShI_arr(fitted_polynomial)[pxl_pos]))
    return image_line


# Function for normalization of image row by row with shadow intensity Px = Px + (1 + Px * ShI)
# ShI - shadow intensity, 1 - (Px(x)/P(0) on a single row (image row)
# ShI - its value tells about mean % reduction of pixel intensity in given position
def normalize_img_RBR(image, fit_degree):
    st_time = datetime.datetime.now()
    for pxl_row in image:
        normalize_img_line(pxl_row, row_polynom_vals(image, pxl_row, fit_degree))
    print(f"Image processing (normalization) time: {datetime.datetime.now() - st_time} (H:M:S)")
    return image



# Normalize the image by a single, specified row
def normalize_img_ByRow(image, row, fit_degree):
    st_time = datetime.datetime.now()
    for pxl_pos in image:
        normalize_img_line(pxl_pos, row_polynom_vals(image, row, fit_degree))
    print(f"Image processing (normalization) time: {datetime.datetime.now() - st_time} (H:M:S)")
    return image
