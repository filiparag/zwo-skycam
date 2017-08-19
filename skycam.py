#!/usr/bin/env python3

import os
import time
import zwoasi as asi
from threading import Thread
from queue import Queue

class SkyCam:
    """ SkyCam is an abstraction layer for zwoasi Python bindings 
    """

    @staticmethod
    def initialize(_library=None):
        """ Initialize ZWOASI SDK library

        The official SDK library can be obtained from this link:
        https://astronomy-imaging-camera.com/tets1/

        Args:
            _library (str): ovveride default location for the library
        
        """

        if _library is None:
            _library = os.path.dirname(os.path.realpath(__file__))\
                       + '/asi.so'

        asi.init(_library)


    @staticmethod
    def cameras():
        """ List of conneted cameras

        Returns:
            list: List of camera names as sttings
        
        """

        return asi.list_cameras()


    def __init__(self, _camera_id, _bandwidth=80):
        """ Initializes a SkyCam camera object

        This funtion automatically calls configure() which sets camera 
        parameters to default settings.

        Args:
            _camera_id (int): Camera ID in the cameras() list or it's name
        
        """

        self.camera = asi.Camera(_camera_id)
        self.camera_info = self.camera.get_camera_property()
        self.camera.set_control_value(asi.ASI_BANDWIDTHOVERLOAD, _bandwidth)
        self.camera.stop_video_capture()
        self.camera.stop_exposure()
        self.configure()


    def configure(self, _gain=150, _exposure=1000000, _wb_b=99, \
                  _wb_r=75, _gamma=60, _brightness=50, _flip=0, \
                  _bin=1, _roi=None, _drange=8, \
                  _color=False, _mode='video'):
        """ Used to change camera parameters

        Args:
            _gain (int): Camera gain
            _exposure (int): Camera exposure in microseconds
            _wb_b (int): Camera whitebalance
            _wb_r (int): Camera whitebalance
            _gamma (int): Camera gamma
            _brightness (int): Camera brightness
            _flip (int): Picture flip, valuse can be 0 or 1
            _bin (int): Picture binning, values can be 1 or 2
            _roi (tuple): Region of interest, formatted as a 
                          tuple (x, y, width, height)
            _drange (int): Dynamic range, value can be 8 or 16 bits
            _color (bool): Camera oolor mode
            _mode (str): Capturing mode, value can be 'video' or 'piture'
                         If set to 'picture', apturing is a lot slower.

        """
        
        self.camera.stop_exposure()

        if _mode == 'video':
            self.camera.start_video_capture()
        elif _mode == 'picture':
            self.camera.stop_video_capture()
        self.mode = _mode

        self.camera.set_control_value(asi.ASI_GAIN, _gain)
        self.camera.set_control_value(asi.ASI_EXPOSURE, _exposure)
        self.camera.set_control_value(asi.ASI_WB_B, _wb_b)
        self.camera.set_control_value(asi.ASI_WB_R, _wb_r)
        self.camera.set_control_value(asi.ASI_GAMMA, _gamma)
        self.camera.set_control_value(asi.ASI_BRIGHTNESS, _brightness)
        self.camera.set_control_value(asi.ASI_FLIP, _flip)

        if _roi is None:
            _roi = (
                0, 0, 
                int(self.camera_info['MaxWidth'] / _bin), 
                int(self.camera_info['MaxHeight'] / _bin)
            )

        self.camera.set_roi(start_x=_roi[0], start_y=_roi[1],\
            width=_roi[2], height=_roi[3], bins=_bin)

        if _color is True:
            self.camera.set_image_type(asi.ASI_IMG_RGB24)

        else:
            if _drange is 8:
                self.camera.set_image_type(asi.ASI_IMG_RAW8)
            elif _drange is 16:
                self.camera.set_image_type(asi.ASI_IMG_RAW16)


    def capture(self, _directory=None, _file=None, _format='.jpg'):
        """ Frame capturing function

        If both _directory and _file are not declared, it will return 
        the picture as an array. Otherwise, undeclared parameters will
        fall back to default values.

        Args:
            _directory (str): Path for saving captured photos
            _file (str): File name, strftime formatting is enabled
                         Formatting instrutions: http://strftime.org/
            _format (str): Indiates piture format, default is JPEG

        Returns:
            numpy array: If both _directory and _file are not declared
        
        """
        
        if _file is None and _directory is not None:
            _file = self.camera_info['Name'].replace(' ', '-') \
                    + '-%Y-%m-%d-%H-%M-%S-%Z' + _format

        if _directory s None and _file is not None:
            if not os.path.isdir('/tmp/skycam/'):
                os.makedirs('/tmp/skycam', 755)
            _directory = '/tmp/skycam/'

        if _file is not None and _directory is not None:
        
            _file = time.strftime(_file)

            if self.mode == 'picture':
                self.camera.capture(filename=\
                    (_directory + '/' + _file))
            elif self.mode == 'video':
                self.camera.capture_video_frame(filename=\
                    (_directory + '/' + _file))

        else:

            if self.mode == 'picture':
                return self.camera.capture()
            elif self.mode == 'video':
                return self.camera.capture_video_frame()


    def timelapse(self, _action, _directory=None, _file=None,\
                  _format='.jpg', _delay=0):
        """ Automatic frame capturing in a separate thread

        Args:
            _action (str): Timelapse control
                           'start' starts the timelapse
                           'stop'  stops the timelapse and 
                                   clears frame buffer
                           'pause' pauses the timelapse
                           'next'  retrieves next frame
                           'all    retrieves all frames
            _directory (str): Path for saving captured photos
            _file (str): File name pattern, strftime formatting is enabled
            _format (str): Indiates piture format, default is JPEG
            _delay (int): Time delay between two exposures in milliseonds

        Returns:
            If _action is 'next' it will return the oldest frame in the 
            queue and remove it from the queue.

            If _action is 'all' it will return all queued frames in an 
            age-ordered ascending list. Calling this doesn't clear the
            frame queue.
        
        """

        if _action == 'start':

            if _directory is None and _file is None:
                self.timelapse_buffer = Queue()

            self.recorder = Thread(target=self.timelapse_recorder,\
                            args=(_directory, _file, _format, _delay))
            self.recorder.daemon = True
            self.timelapse_active = True
            self.recorder.start()

        elif _action == 'stop' or 'pause':

            self.timelapse_active = False
            self.recorder.join()

            if _action == 'stop':
                try:
                    self.timelapse_buffer.clear()

        elif _action == 'next':

            # TODO: Add support for non-buffer timelapses

            return self.timelapse_buffer.get()

        elif _action == 'all':

            # TODO: Add support for non-buffer timelapses

            return list(self.timelapse_buffer.queue)

        # TODO: Add option to clear frame buffer


    def timelapse_recorder(self, _directory=None, _file=None,\
                           _format='.jpg', _delay=0):
        """ Timelapse background thread

        This funtion souldn't be called. Use timelapse() instead. 

        Args:
            _directory (str): Path for saving captured photos
            _file (str): File name pattern, strftime formatting is enabled
            _format (str): Indiates piture format, default is JPEG
            _delay (int): Time delay between two exposures in milliseonds

        """

        if _directory is None and _file is None:
            while self.timelapse_active:
                frame = self.capture()
                self.timelapse_buffer.put((frame, time.time()))
                time.sleep(_delay / 1000)
        else:
            while self.timelapse_active:
                self.capture(_directory=_directory, _file=_file, _format=_format)
                time.sleep(_delay / 1000)

