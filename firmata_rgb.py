#!/usr/bin/env python

# RGB random mood lamp on piMagic board
# Uses PWM~ outputs on pins 3, 5 and 6
# @croz_tech            V1.0 21/09/2013
import pyfirmata
import random
import sys
import os
from time import sleep

# Create a board object for the piMagic
board=pyfirmata.Arduino('/dev/ttyAMA0')

# Set up pins
# D3,5,6.. PWM outputs
pin3 = board.get_pin('d:3:p')
pin5 = board.get_pin('d:5:p')
pin6 = board.get_pin('d:6:p')

# Initialise last values to zero (LED elements all off)
oldred=0
oldgreen=0
oldblue=0

# Clear and print some instructions on the screen
os.system ('clear')
print '@croz_tech RGB random mood-lamp using PiMagic PWM...'
print 'Press CTRL+C to exit'
print
print '( R  ,  G  ,  B  )'
while True:
        try:
                # Get some random colours (0..1) levels
                newred=random.randint(0,100)/100.0
                newgreen=random.randint(0,100)/100.0
                newblue=random.randint(0,100)/100.0
                # Loop to fade (interpolate) from old to new colour
                for iter in range(0,11):
                        pin3.write(oldred+((newred-oldred)*(float(iter)/10)))
                        pin5.write(oldgreen+((newgreen-oldgreen)*(float(iter)/10)))
                        pin6.write(oldblue+((newblue-oldblue)*(float(iter)/10)))
                        # Adjust this (default=0.2sec) for slower/faster transition
                        sleep(0.2)
                # Display the new colour for debug
                print '(%.2f, %.2f, %.2f)' % (newred, newgreen, newblue)
                # Store this for the next transistion
                oldred=newred
                oldgreen=newgreen
                oldblue=newblue
                # Adjust this (default=2sec) for more/less frequent colour changes
                sleep (2)
        except KeyboardInterrupt:
                # CTRL+C interrupt - turn off LEDs and shut down nicely
                pin3.write(0)
                pin5.write(0)
                pin6.write(0)
                board.exit()
                print ' exit'
                print
                sys.exit()
