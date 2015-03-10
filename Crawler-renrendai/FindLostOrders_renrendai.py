#! /usr/bin/python3.4
# -*- coding: utf-8 -*-

__author__ = 'WangMiaofei'

import os, csv

if __name__ == '__main__':
    print('******************************************************')
    print('*Renrendai Tools for Finding lost orders in csv v0307*')
    print('******************************************************'+'\n')
    while True:
        try:
            raw_input = input("Input the csv file name:")
            print(os.getcwd()+'/'+raw_input)
            reader = csv.DictReader(open(os.getcwd()+'/'+raw_input, 'r'))
            print("Correct file name.")
            writer = open(os.getcwd()+"/LostOrder_"+raw_input+'.txt', 'w')
            break
        except:
            import traceback
            print(traceback.format_exc())

    lineCount = 0
    rawList = []
    for item in reader:
        lineCount += 1
        rawList.append(int(item['序号']))
    rawList.sort()
    lasti = rawList[0]
    for i in rawList[1:]:
        lasti += 1
        #print(i)
        while(i > lasti):
            writer.write(str(lasti)+'\n')
            lasti += 1

    writer.close()
    print("Finished.")