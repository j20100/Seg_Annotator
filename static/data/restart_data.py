#!/usr/bin/env python
import os
import cv2
import glob
import numpy as np

path_annotator = '/home/jonathan/Seg_Annotator/static/data/'
searchannot = os.path.join( path_annotator , "annotations" , "*.png_corrected_*" )
fileannot = glob.glob(searchannot)
fileannot.sort()
for i in range(len(fileannot)):
    t = fileannot[i].split('/')
    k=t[7].split('.')
    name="/"+t[1]+"/"+t[2]+"/"+t[3]+"/"+t[4]+"/"+t[5]+"/"+t[6]+"/"+k[0]+".png"
    print(name)

    img = cv2.imread(fileannot[i])
    cv2.imwrite(name,img)
