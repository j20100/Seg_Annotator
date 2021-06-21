#!/usr/bin/env python
import os
import cv2
import glob
import numpy as np


#For annotator
void = [0,0,0]
bean = [0,0,1]
notabean = [0,0,2]

label_colours = np.array([void, bean, notabean])

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

    b = img[:,:,2].copy()
    print(b.shape)
    for l in range(len(label_colours)):
        b[img[:,:,2]==l]=label_colours[l,2]

    rgb = np.zeros((img.shape[0], img.shape[1], 3))
    rgb[:,:,0] = (0)#[:,:,0]
    rgb[:,:,1] = (0)#[:,:,1]
    rgb[:,:,2] = (b)#[:,:,2]

    cv2.imwrite(name,rgb)
