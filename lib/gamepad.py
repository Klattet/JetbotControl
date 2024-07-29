import struct
from threading import Thread
from typing import Callable
from io import TextIOWrapper

__all__ = "Gamepad",

class Gamepad:

    def __init__(self, gamepad_number: int = 0, display_events: bool = False):
        """
        Initializes the gamepad.

        Arguments:
            gamepad_number - An integer corresponding to the number assigned to the gamepad in the system.

            display_events - Gamepad events will be printed to the console if set to True.
        """

        self.gamepad_number: int = gamepad_number
        self.display_events: bool = display_events
        self._path: str = f"/dev/input/js{gamepad_number}"
        self._file: TextIOWrapper | None = None

        self.buttons: dict = {}
        self.axes: dict = {}

        self._event_size: int = struct.calcsize("IhBB")

        self.thread_is_running: bool = False
        self.latest_event: Thread | None = None
        self.event_thread: Thread | None = None

    def _event_thread(self) -> None:
        while self.thread_is_running:
            self.latest_event = struct.unpack('IhBB', self._file.read(self._event_size))
            timestamp, value, event_type, index = self.latest_event

            if self.display_events:
                print(f"Timestamp: {timestamp}, Value: {value}, Type: {event_type}, Index: {index}")

            if event_type == 1:
                func_dict = self.buttons
            elif event_type == 2:
                func_dict = self.axes
            else:
                raise RuntimeError(f"Event type {event_type} not recognized.")

            if index not in func_dict:
                func_dict[index] = {"event": None, "callbacks": [], "active": False}

            func_dict[index]["event"] = {"timestamp": timestamp, "value": value, "type": event_type, "index": index}

            for callback, inverted in func_dict[index]["callbacks"]:
                callback()

    def connect(self) -> None:
        self._file = open(self._path, "rb")
        self.event_thread = Thread(target = self._event_thread)
        self.thread_is_running = True
        self.event_thread.start()

    def disconnect(self) -> None:
        self.thread_is_running = False
        self.event_thread.join()
        self.event_thread = None
        self._file.close()
        self._file = None

    def button_bind(self, index: int, callback: Callable, invert: bool = False):
        """Bind a button to an action."""
        self._bind(index, callback, invert, self.buttons)

    def axis_bind(self, index: int, callback: Callable, invert: bool = False):
        """Bind an analog input to an action."""
        self._bind(index, callback, invert, self.axes)

    def _bind(self, index: int, callback: Callable, invert: bool, dictionary: dict):
        if index not in dictionary.keys():
            dictionary[index] = {"event": None, "callbacks": [], "active": False}

        dictionary[index]["callbacks"].append((callback, invert))

    def button_unbind(self, index: int, callback: Callable):
        """Unbind an action from a button."""
        self._unbind(index, callback, self.buttons)

    def axis_unbind(self, index: int, callback: Callable):
        """Unbind an action from an axis."""
        self._unbind(index, callback, self.axes)

    @staticmethod
    def _unbind(index: int, callback: Callable, dictionary: dict):
        for call in dictionary[index]["callbacks"]:
            if call is callback:
                dictionary[index]["callbacks"].remove(call)
                break
        else:
            raise AttributeError(f"{callback} is not bound to {index}.")