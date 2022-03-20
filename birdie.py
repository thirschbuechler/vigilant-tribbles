#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
platform independent notifications using win10toast and gi.notify (windows, linux)

probably same as 
 -https://pypi.org/project/notifier-function/
or
 -https://pypi.org/project/notifier-function/

Created on Mon March 20, 2022
@author: thirschbuechler
"""
from sys import platform

class birdie(object):
    def __init__(self, text, prog_title="title", duration=8, icon=""):
        self.text = text
        self.prog_title = prog_title
        self.duration = duration
        self.icon = icon
        
    def show(self):
        # toDo mqtt ingress / egress for headless/remote

        if platform == "linux" or platform == "linux2":
                import gi
                gi.require_version('Notify', '0.7')
                from gi.repository import Notify
                Notify.init(self.prog_title)
                notice = Notify.Notification.new(self.prog_title, self.text, self.icon)
                                
                # options     
                    
                    # notice.set_urgency(2) # optional - 2 makes no_entry sign, below or omitted its an "i"
                    #notice = Notify.Notification.new("Critical !", msg)
                    # notice.attach_to_status_icon(self.icon)
                    # notice.set_timeout(Notify.EXPIRES_DEFAULT)
                    # notice.set_urgency(Notify.Urgency.LOW)
                    #        n = Notify.Notification.new(title,            text,             '/usr/share/icons/gnome/32x32/places/network-server.png')
                notice.show() # yeah me 5 years ago
        elif platform == "win32":
            from win10toast import ToastNotifier
            toast = ToastNotifier()
            toast.show_toast(
                self.prog_title,
                self.text,
                duration = self.duration,
                icon_path = self.icon, #"icon.ico",
                threaded = True,
            )
        #elif platform == "darwin":
            # apple
            

#-#-# module test #-#-#
if __name__ == '__main__': # test if called as executable, not as library
    b = birdie("peep", "birdie_V1")
    b.show()