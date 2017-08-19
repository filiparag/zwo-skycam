# ZWO SkyCam

An easy to use Python 3 framework for ZWO ASI cameras and Raspberry Pi 3

---

## Installation
### Prerequisites

Updating repositories

`sudo apt update`

Git (optional)

`sudo apt -y install git`

Python 3

`sudo apt -y install python3 pyton3-pip`

Pillow module

`sudo pip3 install Pillow`

### Cloning repository

You can clone this repository by exeuting:

`git lone https://github.com/filiparag/zwo-skycam.git`

or download the archived repository from GitHub website.

## RAMdisk

If you have a slow SD card or just want to store captured frames in RAM, you can run:

`sudo ./ramdisk.sh`

This sript will create a *ramfs* partition mounted at `/mnt/skycam`.

## Usage

To use this framework, copy both `skycam.py` and `asi.so` into the folder of your project. After this, you can import *zwo-skycam* with `import skycam`.

### Initialization

At first, the framework has to establish the onnetion with a camera. This can be done by calling `skycam.initialize( _library )` function, where you can use `_library` parameter to indiate different location of the `asi.so` library.

### Configuration

This framework allows you to easily set camera parameters by calling `skycam.configure( _gain, _exposure, _wb_b, _wb_r, _gamma, _brightness, _flip, _drange, _color )`. Detailed explanation of these parameters an be easily found on ZWO's website. All parameters have predefined values, so if you aren't sure about corret values, just leave them out.

### Capturing a single frame

After initializing and configuring the camera, you can capture individual frames using `capture( _directory, _file, _extension)` function. If you don't supply parameters, default save loation is urrent directory, file name is formatted like in this example `17-08-31-23-05-54-UTC.jpg`. Default file format is JPEG.

### Timelapse

**TODO**