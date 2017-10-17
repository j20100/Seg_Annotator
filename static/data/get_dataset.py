#!/usr/bin/env python
import json
import os
import glob


def sortKeyFunc(s):
    t = s.split('/')
    k=t[7].split('.')
    s=k[0].split('_')
    return int(s[2])

path_annotator = '/home/deepblack/Seg_Annotator/static/data/'
searchimg = os.path.join( path_annotator , "images" , "*.png" )
filename = glob.glob(searchimg)
filename.sort(key=sortKeyFunc)
fileimg = []
fileannot = []
for i in range(len(filename)):
    t = filename[i].split('/')
    k=t[7].split('.')
    nameimg="/"+t[4]+"/"+t[5]+"/"+t[6]+"/"+k[0]+".png"
    nameannot="/"+t[4]+"/"+t[5]+"/"+"annotations"+"/"+k[0]+".png"
    fileimg.append(nameimg)
    fileannot.append(nameannot)


data = {'labels':[
  "road",
  "sidewalk",
  "building",
  "lanemark",
  "fence",
  "pole",
  "trafficlight",
  "trafficsign",
  "vegetation",
  "terrain",
  "sky",
  "person",
  "rider",
  "car",
  "truck",
  "bus",
  "snow",
  "motorcycle",
  "bicycle",
  "void"
],
"imageURLs": fileimg,
"annotationURLs": fileannot
}

with open('dataset.json', 'w') as outfile:
    json.dump(data, outfile)
