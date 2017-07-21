# -*- coding: utf-8 -*-
"""
Created on Thu May 11 22:18:15 2017

@author: seas-oi
"""

import os, os.path, optparse,sys
import glob
import shutil

path1 = os.getcwd()
path2 = os.path.dirname(path1)+"/parametres.txt"
print path2
tiles = open(path2, "r")
for i in range(10):
    line = tiles.readline()
tileList = line.split(",")
tileList[-1] = tileList[-1][:-1]


folderList = glob.glob("./acquisition/*.SAFE")

for folder in folderList:
    listKeep = []
    folderTile = glob.glob(folder+"/GRANULE/*")
    for f in folderTile:
        for tile in tileList:
            if tile in f:
                listKeep.append(f)
    print(listKeep)
    for f in folderTile:
        print(f)
        if f not in listKeep:
            shutil.rmtree(f)
