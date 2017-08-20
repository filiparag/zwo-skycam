#!/usr/bin/env python3

import os
import time
import zwoasi as asi
from threading import Thread
from queue import Queue
from PIL import Image
from glob import glob

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

        This funtion automatically sets camera parameters 
        to default settings. To change them use configure()

        Args:
            _camera_id (int): Camera ID in the cameras() list or it's name
        
        """

        self.camera = asi.Camera(_camera_id)
        self.camera_info = self.camera.get_camera_property()
        self.camera.set_control_value(asi.ASI_BANDWIDTHOVERLOAD, _bandwidth)
        self.camera.stop_video_capture()
        self.camera.stop_exposure()
        self.configure()
        self.frame_buffer = Queue()
        self.frame_counter = 0
        self.recorder = self.Recorder(self)

        self.camera.set_control_value(asi.ASI_GAIN, 150)
        self.camera.set_control_value(asi.ASI_EXPOSURE, 1000000)
        self.camera.set_control_value(asi.ASI_WB_B, 99)
        self.camera.set_control_value(asi.ASI_WB_R, 75)
        self.camera.set_control_value(asi.ASI_GAMMA, 60)
        self.camera.set_control_value(asi.ASI_BRIGHTNESS, 50)
        self.camera.set_control_value(asi.ASI_FLIP, 0)
        self.camera.start_video_capture()
        self.camera.set_image_type(asi.ASI_IMG_RAW8)


    def configure(self, _gain=None, _exposure=None, _wb_b=None,\
                  _wb_r=None, _gamma=None, _brightness=None, _flip=None,\
                  _bin=None, _roi=None, _drange=None,\
                  _color=None, _mode=None):
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
        if _mode is not None:
            self.mode = _mode

        if _exposure is not None:
            self.camera.set_control_value(asi.ASI_EXPOSURE, _exposure)
        if _gain is not None:
            self.camera.set_control_value(asi.ASI_GAIN, _gain)
        if _wb_b is not None:
            self.camera.set_control_value(asi.ASI_WB_B, _wb_b)
        if _wb_r is not None:
            self.camera.set_control_value(asi.ASI_WB_R, _wb_r)
        if _gamma is not None:
            self.camera.set_control_value(asi.ASI_GAMMA, _gamma)
        if _brightness is not None:
            self.camera.set_control_value(asi.ASI_BRIGHTNESS, _brightness)
        if _flip is not None:
            self.camera.set_control_value(asi.ASI_FLIP, _flip)

        if _bin is None:
            _bin = 1

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
            numpy array: If both _directory and _file are not declared, 
            it will only return the picture as an array.
        
        """
        
        if _file is None and _directory is not None:
            _file = self.camera_info['Name'].replace(' ', '-') \
                    + '-%Y-%m-%d-%H-%M-%S-%Z-' +\
                    str(self.frame_counter) + _format

            self.frame_counter += 1

        if _directory is None and _file is not None:
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

        if self.mode == 'picture':
            return self.camera.capture()
        elif self.mode == 'video':
            return self.camera.capture_video_frame()


    class Recorder:

        """ Recorder is used to record continuous 
            frames automatically

        Note that Recorder class gets isntanced as 
        SkyCam.recorder object.

        """

        def __init__(self, _owner):

            """ Sets all variables to default state

            """

            self.owner = _owner
            self.buffer = Queue()
            self.recording = False

            self.delay = 0
            self.directory = None
            self.file = None
            self.format = None
            self.keep = True
            self.save = False


        def configure(self, _delay=None, _keep=None, _save=None,\
                      _directory=None, _file=None, _format=None):

            """ Configure SkyCam recorder

            Args:
                _delay (int): Delay between frames in milliseconds
                _keep (bool): Indicates whether to keep frames 
                              in RAM buffer
                _save (bool): Indicates whether to keep frames 
                              to storage device
                _directory (str): Path for saving captured photos
                _file (str): File name, strftime formatting is enabled
                             Formatting instrutions: http://strftime.org/
                _format (str): Indiates piture format, default is JPEG
            
            """

            if _delay is not None:
                self.delay = _delay
            if _directory is not None:
                self.directory = _directory
            if _file is not None:
                self.file = _file
            if _format is not None:
                self.format = _format
            if _keep is not None:
                self.keep = _keep
            if _save is not None:
                self.save = _save


        def record(self):

            """ Recorder background thread

            Do not call this method directly. Use start() instead.
            
            """

            while self.recording:

                if self.save:
                    _frame = self.owner.capture(_directory=self.directory,\
                        _file=self.file, _format=self.format)
                else:
                    _frame = self.owner.capture()

                if self.keep:
                    self.buffer.put((_frame, time.time()))

                time.sleep(self.delay / 1000)


        def start(self):
            
            """ Starts background thread for recording
            
            """

            self.recorder = Thread(target=self.record, args=())
            self.recording = True
            self.recorder.start()


        def stop(self):

            """ Stops background thread for recording
            
            """

            self.recording = False
            self.recorder.join()


        def buffer_is_empty(self):

            """ Ckeck if buffer is empty
            
            """

            return self.buffer.empty()

        
        def buffer_next(self):

            """ Returns oldest frame in the buffer

            Calling this method requires _keep to be True.
            Returned frame gets removed from the buffer.
            
            """

            return self.buffer.get_nowait()


        def buffer_all(self):

            """ Returns all frames stored in the buffer

            Calling this method requires _keep to be True.
            
            """

            return list(self.buffer.queue)

        
        def buffer_clear(self):

            """ Clears the buffer
            
            """

            self.buffer.clear()

        
        def buffer_load(self):

            """ Loads all frames stored in _directory 
            into the buffer.

            Calling this method requires _directory to be
            defined to an existing direcotry.
            
            """

            _files = glob(self.directory)
            print(_files)