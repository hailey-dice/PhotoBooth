#Creates a branded photobooth strip of photos from RPi camera

import PIL
from PIL import Image
from PIL import ImageOps
from picamera import PiCamera
import RPi.GPIO as GPIO 
from time import sleep
from twython import Twython 
import datetime
import os

SIZE = 500, 500
LOGOSIZE = 50,50
camera = PiCamera()

C_key = "9MJQA4UzLCbrgnCb17RX3Wykn" 
C_secret = "gK1Ye6nsPotsXypfSyyfHiyi4lx2YuHaJymIGOa4cRhByhmYfB" 
A_token = "619219844-UgfCGDHho5FkyDk4umxek1cgYCz0HNdFx8XwjVy8" 
A_secret = "G2YKIaSUF0I054WOyZzPnugAN54yTWexJ87Y8kvgdCs9V" 

TOP = 27 
MID = 17
BOT = 24
TL = 26 #top left
TR = 4 #top right
BL = 23 #bottom left
BR = 22 #bottom right
COMD1 = 25 #common cathode for digit 1

GPIO.setwarnings(False) # Ignore warnings
GPIO.setmode(GPIO.BCM) # Use BCM Pin numbering
GPIO.setup(16, GPIO.IN)

GPIO.setup(COMD1, GPIO.OUT, initial=GPIO.HIGH)

#Anode for Segments
GPIO.setup(TOP, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(BOT, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(MID, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(TL, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(TR, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(BL, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(BR, GPIO.OUT, initial=GPIO.LOW)


digits = {0: [TOP, BOT, TR, TL, BR, BL],
          1: [TR, BR],
          2: [TOP, TR, MID, BL, BOT],
          3: [TOP, MID, BOT, TR, BR],
          4: [TL, MID, TR, BR],
          5: [TOP, TL, MID, BR, BOT],
          6: [TOP, TL, MID, BL, BOT, BR],
          7: [TOP, TR, BR],
          8: [TOP, MID, BOT, TR, TL, BR, BL],
          9: [TOP, MID, TL, TR, BR]
        }


def buttonOne_callback(channel):
    print ("Button Pressed") 
    loc = getDir()
    takePhotos(loc)
    im = mergeImage("{}/0.jpg".format(loc), "{}/1.jpg".format(loc), "{}/2.jpg".format(loc), "{}/3.jpg".format(loc), "/home/dice/Pictures/su1.png")
    img_with_border = ImageOps.expand(im,border=30,fill='red')
    path = '{}/strip.jpg'.format(loc)
    img_with_border.save(path)
    sendTweet(path)
    
GPIO.add_event_detect(16, GPIO.RISING, callback=buttonOne_callback, bouncetime=10000)   


def clearDigit():
    GPIO.output(TOP, GPIO.LOW)
    GPIO.output(MID, GPIO.LOW)
    GPIO.output(BOT, GPIO.LOW)
    GPIO.output(TR, GPIO.LOW)
    GPIO.output(BR, GPIO.LOW)
    GPIO.output(BL, GPIO.LOW)
    GPIO.output(TL, GPIO.LOW)
    
def displayNum(num):
    segs = digits[num]
    for seg in segs:
        GPIO.output(seg, GPIO.HIGH)
        

def mergeImage(file1, file2, file3, file4, logoImage):
    image1 = Image.open(file1)
    image1.resize(SIZE)
    
    image2 = Image.open(file2)
    image2.resize(SIZE)
    
    image3 = Image.open(file3)
    image3.resize(SIZE)
    
    image4 = Image.open(file4)
    image4.resize(SIZE)
    
    logo = Image.open(logoImage)
    logo.resize(LOGOSIZE)
    
    finalWidth = 500*4
    
    strip = Image.new('RGB', (finalWidth, 500))
    strip.paste(im=image1, box=(0,0))
    strip.paste(im=image2, box=(500,0))
    strip.paste(im=image3, box=(1000,0))
    strip.paste(im=image4, box=(1500,0))
    strip.paste(logo, box=(1900, 410))
    
    return strip

def getDir():
    now = datetime.datetime.now()
    newDir = "/home/dice/Pictures/{}-{}-{}-{}-{}-{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
    os.mkdir(newDir)
    return newDir

def takePhotos(loc):
    GPIO.output(COMD1, GPIO.LOW)
    camera.start_preview()
    for i in range (4):
        for n in range(3, 0, -1):
            displayNum(n)
            sleep(1)
            clearDigit()
        camera.capture('{}/{}.jpg'.format(loc, i), resize=(500,500))
    camera.stop_preview()
    
def sendTweet(path):
    myTweet = Twython(C_key,C_secret,A_token,A_secret)

    photo = open(path, 'rb') 
    response = myTweet.upload_media(media=photo)
    myTweet.update_status(status='look i did it', media_ids=[response['media_id']])

    

input("Press Enter to Exit \n")

#loc = getDir()
#takePhotos(loc)
#im = mergeImage("{}/0.jpg".format(loc), "{}/1.jpg".format(loc), "{}/2.jpg".format(loc), "{}/3.jpg".format(loc), "/home/dice/Pictures/su1.png")
#img_with_border = ImageOps.expand(im,border=30,fill='red')
#img_with_border.save('{}/strip.jpg'.format(loc))
