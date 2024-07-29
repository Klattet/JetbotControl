import cv2
from numpy import ndarray, dtype
from typing import Literal, Generator, Any
from threading import Thread

__all__ = "Camera",

class Camera:
    def __init__(self, mode: Literal[0, 1, 2, 3, 4, 5], width: int = None, height: int = None, black_and_white: bool = False):
        """
        Initialize the camera.

        Arguments:
            mode: int - An integer between 0 and 5 inclusive.
                   Represents a builtin camera mode, each having different resolution and fps settings.

                      width: height: fps:
                   0: 3264   2464    21
                   1: 3264   1848    28
                   2: 1920   1080    30
                   3: 1640   1232    30
                   4: 1280   720     60
                   5: 1280   720     120

            width: int - The width of the image outputted.
            If camera mode and image width do not coincide, the image is resized.

            height: int - The height of the image outputted.
            If camera mode and image height do not coincide, the image is resized.

            black_and_white: bool - Whether the outputted image is black and white or colored.

        Note:
            If either only the width is specified, or the height is specified, aspect ratio will be preserved.
            Otherwise, the image will be squished or stretched to fit the new aspect ratio.
        """

        modes = {
            0: (3264, 2464, 21),
            1: (3264, 1848, 28),
            2: (1920, 1080, 30),
            3: (1640, 1232, 30),
            4: (1280, 720, 60),
            5: (1280, 720, 120)
        }
        self.mode, self.width, self.height, self.black_and_white = mode, width, height, black_and_white
        self.capture_width, self.capture_height, self.capture_fps = modes[mode]

        if width is None:
            self.width = self.capture_width
        if height is None:
            self.height = self.capture_height

        self.init_command = f"nvarguscamerasrc sensor-mode={mode} ! " \
                            f"video/x-raw(memory:NVMM), width={self.capture_width}, height={self.capture_height}, format=\"NV12\", framerate={self.capture_fps}/1 ! " \
                            f"nvvidconv ! video/x-raw, width={width}, height={height}, format=\"{'Y' if black_and_white else 'BGR'}x\" ! videoconvert ! appsink"

        self.capture = cv2.VideoCapture(self.init_command, cv2.CAP_GSTREAMER)

        self.frame_thread: Thread | None = None
        self.frame_thread_is_running: bool = False
        self.skipped_frames: int = 0
        self._latest_image: tuple[int, cv2.Mat | ndarray[Any, dtype] | ndarray] | None = None

    def _frame_thread(self) -> None:
        frame_number: int = 1
        while self.frame_thread_is_running:
            returned, image = self.capture.read()
            if returned:
                self._latest_image = frame_number, image
            else:
                self.skipped_frames += 1
            frame_number += 1

    def connect(self) -> None:
        self.frame_thread = Thread(target = self._frame_thread)
        self.frame_thread_is_running = True
        self.frame_thread.start()

    def disconnect(self) -> None:
        self.frame_thread_is_running = False
        self.frame_thread.join()
        self.frame_thread = None

    @property
    def image(self) -> tuple[int, ndarray]:
        return self._latest_image

    def iterator(self) -> Generator[tuple[int, ndarray]]:
        yield frame_cache := self._latest_image
        while self.frame_thread_is_running:
            if frame_cache[0] != self._latest_image[0]:
                yield self.image