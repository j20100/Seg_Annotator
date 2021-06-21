#!/usr/bin/env python
import json
import os
import glob
from PIL import Image


def sortKeyFunc(s):
    t = s.split('/')
    k=t[7].split('.')
    s=k[0].split('_')
    return int(s[2])

path_annotator = '/home/jonathan/Seg_Annotator/static/data/'
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

    #if not os.path.isfile('/home/jonathan/Seg_Annotator'+nameannot):
    #    im = Image.open('/home/jonathan/Seg_Annotator'+nameimg)
    #    image = Image.new('RGB', im.size)
    #    image.save('/home/jonathan/Seg_Annotator'+nameannot)

data = {'labels':[
  "void",
  "bean",
  "notabean"
],
"imageURLs": fileimg,
"annotationURLs": fileannot
}

with open('dataset.json', 'w') as outfile:
    json.dump(data, outfile)
