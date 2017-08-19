# ZWO SkyCam

An easy to use Python 3 framework for ZWO ASI cameras and Raspberry Pi 3

---

## Installation

This library is mainly intended to be run on Raspbery Pi 3. It should work on other similar ARM platforms without any hiccups, but your mileage may vary.

### Prerequisites

Updating repositories

`sudo apt update`

Git (optional)

`sudo apt -y install git`

Python 3

`sudo apt -y install python3 pyton3-pip`

Modules

`sudo pip3 install Pillow zwoasi`

### Cloning repository

You can clone this repository by executing:

`git lone https://github.com/filiparag/zwo-skycam.git`

or download the archived repository from GitHub website.

## RAMdisk

If you have a slow SD card or just want to store captured frames in RAM, you can run:

`sudo ./ramdisk.sh`

This script will create a *ramfs* partition mounted at `/mnt/skycam`.

## Usage

To use this framework, copy both `skycam.py` and `asi.so` into the folder of your project. After this, you can import *zwo-skycam* with `import skycam`.

### Initialization

At first, the framework has to establish the connetion with a camera. This can be done by calling:

`skycam.initialize( _library )`

function, where you can use `_library` parameter to indicate different location of the `asi.so` library.

### Configuration

This framework allows you to easily set camera parameters by calling:

`skycam.configure( _gain, _exposure, _wb_b, _wb_r, _gamma, _brightness, _flip, _drange, _color )`

Detailed explanation of these parameters an be easily found on ZWO's website. All parameters have predefined values, so if you aren't sure about corret values, just leave them out.

### Capturing a single frame

After initializing and configuring the camera, you can capture individual frames using:

`capture( _directory, _file, _extension)`

function. If you don't supply parameters, default save location is current directory, file name is formatted like in this example `17-08-31-23-05-54-UTC.jpg`. Default file format is JPEG.

### Timelapse

Timelapse mode can automatically capture frames. It is not intended to be used to capture video or fast motion.  

#### Capturing

To start a timelapse, call the funtion:

`timelapse( 'start', _directory, _delay, _extension )`

It will start a new thread in the background. Camera configuration can be modified during an active timelapse recording.

When you want to stop recording, call `timelapse( 'stop' )`.

#### Using captured photos

Recorded timelapse frames can be accessed trough this framework with:

`timelapse( 'fetch', _diretory, _seletion, _delete )`

Selection parameter indicates which frames to return, and it an be `newest`, `oldest` or `all`. Delete parameter lets you delete seleted frames to free up some space. Beside the image BLOB, you get the exact time in the format of UNIX timestamp when the frame was taken.

You can get the number of frames by calling:

`timelapse( 'count', _diretory )`

### Video

Planned for future development.

---

If you have any issuses with the framework or want to improve it, feel free to open an issue or submit a pull request.