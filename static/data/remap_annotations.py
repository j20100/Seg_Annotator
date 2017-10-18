#!/usr/bin/env python
import os
import cv2
import glob
import numpy as np


#For annotator
road = [0,0,0]
sidewalk = [0,0,1]
building = [0,0,2]
wall = [0,0,3]
fence = [0,0,4]
pole = [0,0,5]
trafficlight = [0,0,6]
trafficsign = [0,0,7]
vegetation = [0,0,8]
terrain = [0,0,9]
sky = [0,0,10]
person = [0,0,11]
rider = [0,0,12]
car = [0,0,13]
truck = [0,0,14]
bus = [0,0,15]
train = [0,0,16]
motorcycle = [0,0,17]
bicycle = [0,0,18]
void = [0,0,19]


label_colours = np.array([building, pole, trafficsign, vegetation, sky, pole, \
    rider, car, truck, terrain, sky, person, rider, \
    motorcycle, truck, bus, train, road, bicycle, void])


path_annotator = '/home/deepblack/Seg_Annotator/static/data/'
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
