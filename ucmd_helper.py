#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 16:55:24 2020

@author: thirschbuechler
"""
## Important Note ##
# the "input"-function prevents exception throw
# found out by using the eggclock-helper

import time#testing
from datetime import datetime, date
import numpy as np    



def askandreturn(question="Question", validresults=["yes","no"]): # THIS REQUIRES STRINGS AS INPUT for validresults!!
    #validresults = [str(x) for x in validresults] # typecast internal isse: other datatype returned
    while 1:
        text = input(question+str(validresults))
        if text in validresults:
            return text # exit
        
        
def askandreturnindex(question="Question", validresults=["yes","no"]): # THIS REQUIRES STRINGS AS INPUT for validresults!!
    return(validresults.index(askandreturn(question,validresults)))

def askandreturnbool(question="Question", validresults=["n","y"]):# no 0,1 unfortunately
    return(validresults.index(askandreturn(question,validresults)))
            

def savearray(array, name):
    with open(str(name), "w") as a_file:
        for row in array:
            np. savetxt(a_file, row)

class movingcursor():
    def __init__(self):
        self.statstate=0
    
    def state(self):
        if self.statstate==0:
            s="|"
            self.statstate+=1
        elif self.statstate==1:
            s="\\"
            self.statstate+=1
        elif self.statstate==2:
            s="-"
            self.statstate+=1
        elif self.statstate==3:
            s="/"
            self.statstate=0            
        return s

    def write(self, stuff):
        print("\r"+stuff+self.state(), end="")


class today():
    def __init__(self):
        self.today = date.today()    
    
    def date(self):    
        return self.today.strftime("%Y-%m-%d")
    def weekday(self):
        return self.today.strftime('%a')
    
    def time(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        return current_time

        
if __name__ == '__main__': # test if called as executable, not as library
    options = ["yes","no","definitely"]
    options.append("maybe")
    
    print(askandreturn("Continue?",options))
    
    print(askandreturnindex("Continue?",options))
    
    td=today()
    print(td.weekday(),td.date())
    
    cursor=movingcursor()
    printstatusstr = cursor.write

    while True:
        printstatusstr(td.time()+" spin longer..")
        time.sleep(.5)
    
    
    