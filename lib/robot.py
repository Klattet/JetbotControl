import sys, cv2
from typing import Optional, Union
from .gamepad import Gamepad
from .camera import Camera
from numpy import ndarray
from time import sleep

from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

__all__ = "Robot",

class Robot:
    FORWARD = 2
    BACKWARD = 1
    BRAKE = 3
    RELEASE = 4

    def __init__(self):

        self.motor_hat: Adafruit_MotorHAT = Adafruit_MotorHAT(i2c_bus = 1)
        self.left_motor: Adafruit_DCMotor = self.motor_hat.getMotor(1)
        self.right_motor: Adafruit_DCMotor = self.motor_hat.getMotor(2)

        self._camera: Camera | None = None
        self._gamepad: Gamepad | None = None

    @property
    def camera(self) -> Camera:
        if self._camera is None or not self._camera.capture.isOpened():
            raise RuntimeError("Camera has not yet been initialized.")
        else:
            return self._camera

    @property
    def gamepad(self) -> Gamepad:
        if self._gamepad is None:
            raise RuntimeError("Gamepad has not yet been initialized.")
        else:
            return self._gamepad

    def init_camera(self, mode: "0, 1, 2, 3, 4, 5", width: Optional[int] = None, height: Optional[int] = None, black_and_white: bool = False) -> Camera:
        f"""{Camera.__init__.__doc__}"""
        if self._camera is None:
            self._camera = Camera(mode, width, height, black_and_white = black_and_white)
        elif self._camera.capture.isOpened() is False:
            self._camera.capture.open(self._camera.init_command, cv2.CAP_GSTREAMER)
        else:
            raise RuntimeError("Camera is already initialized.")

        return self._camera

    def init_gamepad(self, gamepad_number: int = 0, display_events: bool = False, joystick_movement = False) -> Gamepad:
        f"""{Gamepad.__init__.__doc__}"""
        if self._gamepad is None:
            self._gamepad = Gamepad(gamepad_number, display_events)
        else:
            raise RuntimeError("Gamepad is already initialized.")

        return self._gamepad

    def shutdown(self):
        """Safely shuts down all processes."""
        if self._camera is not None:
            self._camera.disconnect()
            self._camera = None

        if self._gamepad is not None:
            self._gamepad.disconnect()
            self._gamepad = None

        sys.exit("Shutdown command issued.")

    # QR CODE
    @staticmethod
    def read_qr(image: ndarray) -> str:
        return cv2.QRCodeDetector().detectAndDecode(image)[0]

    def process_qr_codes(self, yield_empty = False) -> str:
        for _, image in self.camera.iterator():
            message = self.read_qr(image)
            if message != "" or message == "" and yield_empty:
                yield message

    # MOVEMENT
    def set_speeds(self, left: float, right: float):
        if not -1.0 <= left <= 1.0 or not -1.0 <= right <= 1.0:
            raise AttributeError("Left or right values must be a float or integer between -1.0 and 1.0 inclusive.")

        if 0 < left:
            self.left_motor.run(self.FORWARD)
        elif 0 > left:
            self.left_motor.run(self.BACKWARD)
        else:
            self.left_motor.run(self.RELEASE)

        if 0 < right:
            self.right_motor.run(self.FORWARD)
        elif 0 > right:
            self.right_motor.run(self.BACKWARD)
        else:
            self.right_motor.run(self.RELEASE)

        self.left_motor.setSpeed(int(abs(left) * 255))
        self.right_motor.setSpeed(int(abs(left) * 255))

    def stop(self):
        self.set_speeds(0, 0)

    def forward(self, speed: float, duration: Union[int, float] = 0.0):
        self.set_speeds(speed, speed)
        if duration > 0.0:
            sleep(duration)
            self.stop()

    def backward(self, speed: float, duration: Union[int, float] = 0.0):
        self.set_speeds(-speed, -speed)
        if duration > 0.0:
            sleep(duration)
            self.stop()

    def left(self, speed: float, counter_steer: float = 0.0, duration: Union[int, float] = 0.0):
        self.set_speeds(speed * counter_steer, speed)
        if duration > 0.0:
            sleep(duration)
            self.stop()

    def right(self, speed: float, counter_steer: float = 0.0, duration: Union[int, float] = 0.0):
        self.set_speeds(speed, speed * counter_steer)
        if duration > 0.0:
            sleep(duration)
            self.stop()
