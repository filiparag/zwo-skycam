# ZWO SkyCam

SkyCam module is an abstration layer for Python [zwoasi](https://github.com/stevemarple/python-zwoasi) binding.

## Installation

This library is mainly intended to be run on Raspbery Pi 3. It should work on other similar ARM platforms without any hiccups, but your mileage may vary.

### Prerequisites

Updating repositories

`sudo apt update`

Git (optional)

`sudo apt -y install git`

Python 3

`sudo apt -y install python3 pyton3-pip libusb-1.0-0`

Modules

`sudo pip3 install Pillow zwoasi`

### Cloning repository

You can clone this repository by executing:

`git clone https://github.com/filiparag/zwo-skycam.git`

or download the archived repository from GitHub website.

## RAMdisk

If you have a slow SD card or just want to store captured frames in RAM, you can run:

`sudo ./ramdisk.sh`

This script will create a *ramfs* partition mounted at `/mnt/skycam`.

## Usage

To use this framework, copy both `skycam.py` and `asi.so` into the folder of your project. After this, you can import *zwo-skycam* with `from skycam import SkyCam`.

### Initialization

At first, the framework has to establish the connetion with a camera. This can be done by calling:

`SkyCam.initialize( _library )`

function, where you can use `_library` parameter to indicate different location of the `asi.so` library.

### Configuration

Use `SkyCam.cameras()` to see the list of connected cameras. Select one from the list and create its object like following:

`my_camera = SkyCam('ZWO ASI120MM')`

Camera is now ready to be used. If you want to change any of the settings, you can do it with

`configure( _gain, _exposure, _wb_b, _wb_r, _gamma, _brightness, _flip, _bin, _roi, _drange=8, _color, _mode )`

Parameter `_mode` has two options: `'picture'` and `'video'`. If you need good framerate, run capturing in video mode, otherwise they should work similarly.

For more details about control, read the *docstring* of the function in `skycam.py`.

### Capturing

To capture a single frame, use `capture( _directory, _file, _format )`. If you don't supply any parameters, this method will return the frame as a NumPy array. File name parameter goes through `strftime()` formatting, so you can easily add time and date.

Default value for `_directory` is current path and for `_file` is like in the following example: `ZWO-ASI174MM-2017-08-19-15-40-55-UTC-12`.

### Recording

Recording mode can be used to automatically capture sequential frames. Before starting a recording session, you need to configure it using:

`recorder.configure( _delay, _keep, _save, _directory, _file, _format )`

After this you can use `recorder.start()` and `recorder.stop()` to start and stop recording.

Method `recorder.buffer_is_empty()` returns whether the buffer is empty. 

Methods `recorder.buffer_next()` and `recorder.buffer_all()` return oldest and all frames in the buffer respectively. Note that `recorder.buffer_next()` erases retrieved image from the buffer.

To clear the buffer, use `recorder.buffer_clear()`. Loading frames saved on storage media can be done using `recorder.buffer_load()`.

---

Detailed explanation for every function can be found in form of *docstrings* in `skycam.py`.