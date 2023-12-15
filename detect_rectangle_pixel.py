#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    detect area of one pixel area of same color (or minimum size space where they reside)

    15.12.23, thirschbuechler
"""
# color masking:
# https://stackoverflow.com/questions/47483951/how-can-i-define-a-threshold-value-to-detect-only-green-colour-objects-in-an-ima/47483966#47483966
# find color range from map in stackoverflow link, or use https://pinetools.com/image-color-picker
#
# blob detection: https://stackoverflow.com/questions/42798659/how-to-remove-small-connected-objects-using-opencv
import cv2
# fix cv2 import issue (https://forum.qt.io/topic/119109/using-pyqt5-with-opencv-python-cv2-causes-error-could-not-load-qt-platform-plugin-xcb-even-though-it-was-found/20)
import os, sys
ci_build_and_not_headless = False
try:
    from cv2.version import ci_build, headless
    ci_and_not_headless = ci_build and not headless
except:
    pass
if sys.platform.startswith("linux") and ci_and_not_headless:
    os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")
if sys.platform.startswith("linux") and ci_and_not_headless:
    os.environ.pop("QT_QPA_FONTDIR")

# proceed importing rest
import numpy as np
import subprocess
import skimage
import imageio.v3 as iio



def detect_colored_area(
        in_name =    "Figure_1.png",
        out_name =   "red2.png",
        minsize = 20,
        hsvmin = (0, 25, 25), hsvmax = (1, 255,255)):
    
    # Read
    img = cv2.imread(in_name)

    # Convert to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Mask dark red
    mask = cv2.inRange(hsv, hsvmin, hsvmax)

    # Slice the mask
    imask = mask>0
    masked = np.zeros_like(img, np.uint8)
    masked[imask] = img[imask]

    # Save tmp
    cv2.imwrite(out_name, masked)

    # Open in skimage
    img = iio.imread(out_name)[:,:,0]

    # Delete non-minimum areas
    out = skimage.morphology.area_opening(img, area_threshold=minsize, connectivity=2)

    # Write result
    iio.imwrite(out_name,out)

    # Remove remaining background
    cmd = f"convert {out_name} -trim +repage {out_name}"
    proc = subprocess.Popen(cmd, shell=True)
    proc.wait()

    # Open result
    img = cv2.imread(out_name)

    # Return shape
    return(img.shape)



if __name__ == '__main__': # test if called as executable, not as library, regular prints allowed
    print(detect_colored_area())