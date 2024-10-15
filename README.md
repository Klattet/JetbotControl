# A library with classes and functions to help control a JetBot.

## Goal
Make it easy to interface with the JetBot in your code so that you can focus on what really matters.

## Background
In college, I had several courses that involved self-driving robots and machine learning. I was lent an [NVIDIA Jetson Nano JetBot](https://github.com/NVIDIA-AI-IOT/jetbot), and I was tasked to make it drive autonomously and avoid obstacles by training an image recognition model.\
\
Since I found the official example code hideous and the use of the [traitlets](https://github.com/ipython/traitlets) library annoying, I decided to make my own module with all the robot interfacing code that I needed at the time.\
\
Someone also told me that it wasn't possible to control the JetBot via gamepad controller directly through the on-board usb ports. So I decided to prove them wrong.

## Features
- Receive input signals directly from an onboard usb gamepad controller.
- Bind custom functions to execute code based on gamepad input, and even change them at run-time.
- Initialise camera and receive the latest image frames through an iterator.
- Drive motors in whichever way you'd like.
- Scan QR codes through the camera to receive commands.

## Dependencies

| Dependency                                                                         | Usecase |
|------------------------------------------------------------------------------------|---|
| [Adafruit_MotorHAT](https://github.com/adafruit/Adafruit-Motor-HAT-Python-Library) | A depreciated version of the Adafruit MotorHAT library used to interface with the motors. |
| [numpy](https://github.com/numpy/numpy) | To work with the image data delivered by OpenCV that is in numpy matrices format. |
| [OpenCV-Python](https://github.com/opencv/opencv-python) | To read images from the camera and to scan QR codes. |


After cloning this repo, I recommend creating a virtual environment with:
```commandline
python -m venv .venv
```
Then activating it with:
```commandline
source .venv/bin/activate
```

Run the command below to install dependencies.
```commandline
pip install -r requirements.txt
```
