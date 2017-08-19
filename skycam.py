#!/usr/bin/env python3

import os
import sys
import time
from PIL import Image
import zwoasi as asi
from threading import Thread


# Initialize camera
def initialize(_library=(os.path.dirname(os.path.realpath(__file__)) + '/asi.so')):

    asi.init(_library)

    num_cameras = asi.get_num_cameras()
    if num_cameras == 0:
        raise Exception('No cameras found')
    if num_cameras > 1:
        raise Exception('Only one camera is allowed')

    cameras_found = asi.list_cameras()

    global camera, camera_info
    camera = asi.Camera(0)
    camera_info = camera.get_camera_property()

    camera.set_control_value(asi.ASI_BANDWIDTHOVERLOAD, camera.get_controls()['BandWidth']['MinValue'])

    camera.stop_video_capture()
    camera.stop_exposure()


# Configure camera settings
# _drange must be either 8 or 16
# _oolor is a boolean
def configure(_gain=150, _exposure=30000, _wb_b=99, \
              _wb_r=75, _gamma=60, _brightness=50, _flip=0, \
              _drange=8, _color=False):

    global camera
    camera.set_control_value(asi.ASI_GAIN, _gain)
    camera.set_control_value(asi.ASI_EXPOSURE, _exposure)
    camera.set_control_value(asi.ASI_WB_B, _wb_b)
    camera.set_control_value(asi.ASI_WB_R, _wb_r)
    camera.set_control_value(asi.ASI_GAMMA, _gamma)
    camera.set_control_value(asi.ASI_BRIGHTNESS, _brightness)
    camera.set_control_value(asi.ASI_FLIP, _flip)

    camera.set_control_value(asi.ASI_BANDWIDTHOVERLOAD, 80)

    global drange, color
    color = _color
    drange = _drange


# Capture a single frame and save it to a file
def capture(_directory='./', _file=None, _extension='.jpg'):

    if _file is None:
        _file = time.strftime('%Y-%m-%d-%H-%M-%S-%Z')

    filename = _directory + '/' + _file + _extension

    global camera, drange, color

    if color is True:
        camera.set_image_type(asi.ASI_IMG_RGB24)
    else:
        if drange is 8:
            camera.set_image_type(asi.ASI_IMG_RAW8)
        elif drange is 16:
            camera.set_image_type(asi.ASI_IMG_RAW16)

    camera.capture(filename=filename)


# Recording process function
# Use timelapse function to start reording
def record(_directory, _delay, _extension):

    global recorder
    while recorder[1]:
        filename = str(time.time()).replace('.', '_')
        capture(_directory=_directory, _file=filename, _extension=_extension)
        time.sleep(_delay / 1000)


# Run a background proess for creating a timelapse
# Uses a RAM disk by default
# _delay is time in milliseconds between expositions
def timelapse(_action='start', _directory='/mnt/skycam', _delay=0, _extension='.jpg', _selection='newest', _delete=False):

    # Start the timelapse
    # Starts a timelapse in the bakground
    def start():

        if not os.path.exists(_directory):
            raise Exception('Timelapse diretory does not exsist')

        global recorder
        recorder = [Thread(target=record, args=(_directory, _delay, _extension)), True]
        recorder[0].daemon = True
        recorder[0].start()

    # Stops the timelapse
    def stop():

        global recorder     
        recorder[1] = False
        recorder[0].join()

    # Returns the number of frames in the timelapse
    def count(_directory):

        return len(os.listdir(_directory))

    # Returns a frame from the timelapse
    # _selection can be 'oldest', 'newest' or 'all'
    def fetch(_selection, _delete, _directory):

        frames = os.listdir(_directory)

        if len(frames) == 0:
            raise Exception('No frames availabe to fetch')

        if _selection == 'all':

            frames = sorted(frames)
            
            images = []

            for frame in frames:

                images.append((
                    Image.open(_directory + '/' + frame),
                    float(os.path.splitext(frame)[0].replace('_', '.'))
                ))

                if _delete:
                    os.remove(_directory + '/' + frame)

            return images

        else:
            
            if _selection == 'newest':
                filename = max(frames)
            elif _selection == 'oldest':
                filename = max(frames)

            image = Image.open(_directory + '/' + filename)
            timestamp = float(os.path.splitext(filename)[0].replace('_', '.'))

            if _delete:
                os.remove(_directory + '/' + filename)

            return (image, timestamp)


    if _action == 'start':
        start()
    elif _action == 'stop':
        stop()
    elif _action == 'fetch':
        return fetch(_selection, _delete, _directory)
    elif _action == 'count':
        return count(_directory)