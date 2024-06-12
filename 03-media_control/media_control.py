import cv2
import cv2.aruco as aruco
import sys
import cv2
import json
from matplotlib import pyplot as plt
import numpy as np
import os
import random
import pyglet
from PIL import Image

from keras.models import load_model
from pynput import keyboard
from pynput.keyboard import Controller, Key

keyboard_controller = Controller()

#Media keys created with chatgpt.
# Define the media key for play/pause and volume up and down
# Note: Media keys can be different on different keyboards/OS. Adjust as needed.
media_play_pause_key = Key.media_play_pause
volume_up_key = Key.media_volume_up
volume_down_key = Key.media_volume_down
video_id = 0
if len(sys.argv) > 1:
    video_id = int(sys.argv[1])
current_dir = os.path.dirname(__file__)
model_p = os.path.join(current_dir,'3_value_model.h5')
if os.path.isfile(model_p):
    model = load_model(model_p) 
else:
    print("Model file not found.")
    
COLOR_CHANNELS = 3
IMG_SIZE = 64
SIZE = (IMG_SIZE, IMG_SIZE)

cap = cv2.VideoCapture(video_id)
label_names = ['like','no_gesture','dislike','stop_play']

#Adding pyglet image for debuging  
def cv2glet(img,fmt):
    '''Assumes image is in BGR color space. Returns a pyimg object'''
    if len(img.shape) == 3:
        rows, cols, channels = img.shape
        if fmt == 'BGR':
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    elif fmt == 'GRAY':
      print(img.shape)
      rows, cols = img.shape
      channels = 1
    else:
      rows, cols, channels = img.shape

    raw_img = Image.fromarray(img).tobytes()

    top_to_bottom_flag = -1
    bytes_per_row = channels*cols
    pyimg = pyglet.image.ImageData(width=cols, 
                                   height=rows, 
                                   fmt=fmt, 
                                   data=raw_img, 
                                   pitch=top_to_bottom_flag*bytes_per_row)
    return pyimg

WINDOW_WIDTH = 64
WINDOW_HEIGHT = 64
cooldown_start = 5
cooldown = cooldown_start




cap = cv2.VideoCapture(0)

def record():
    global cooldown
    global cooldown_start
    #get image and perform prediction on it.
        
    print(cooldown)
    ret, frame = cap.read()
    if COLOR_CHANNELS == 1:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    plt.imshow(frame)
    resized = cv2.resize(frame, SIZE)
    
    reshaped = resized.reshape(-1, IMG_SIZE, IMG_SIZE, COLOR_CHANNELS)
    #print("shape")
    #print(reshaped.shape)
    prediction = model.predict(reshaped)
    #print(prediction)
    #print(label_names[np.argmax(prediction)], np.max(prediction))
    prediction_name = label_names[np.argmax(prediction)]
    
    if prediction_name == 'like':
        if cooldown == 0:
            #how to do the keyboard press and releas was done with chatgpt.
            keyboard_controller.press(volume_up_key)
            keyboard_controller.release(volume_up_key)
            print("like")
            cooldown = cooldown_start
        else: 
            cooldown -=1
    elif prediction_name == 'no_gesture':
        print("nothing")
        cooldown = 0
        pass
    elif prediction_name == 'dislike':
        if cooldown == 0:
            keyboard_controller.press(volume_down_key)
            keyboard_controller.release(volume_down_key)
            print("dislike")
            cooldown = cooldown_start
        else: 
            cooldown -=1
        pass
    elif prediction_name == 'stop_play':
        if cooldown == 0:
            keyboard_controller.press(media_play_pause_key)
            keyboard_controller.release(media_play_pause_key)
            print("stop_play")
            cooldown = cooldown_start
        else: 
            cooldown -=1
        pass
    
    
    
    return reshaped[0]
    pass



#for debug switch commented and uncommented parts->

while True:
    record()

#pyglet.app.run()
#window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
#@window.event
#def on_draw():
#    window.clear()
#    frame = record()
#    #frame.draw()
#    img = cv2glet(frame, 'BGR')
#    img.blit(0, 0, 0)


cap.release()