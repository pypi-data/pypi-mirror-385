from typing import Any

from bluer_algo.socket.classes import SocketComm, DEV_HOST
from bluer_sbc.imager.camera import instance as camera
from bluer_sbc.env import BLUER_SBC_ENV

from bluer_ugv.swallow.session.classical.keyboard import ClassicalKeyboard
from bluer_ugv.swallow.session.classical.leds import ClassicalLeds
from bluer_ugv.swallow.session.classical.setpoint.classes import ClassicalSetPoint
from bluer_ugv.logger import logger


class ClassicalCamera:
    def __init__(
        self,
        keyboard: ClassicalKeyboard,
        leds: ClassicalLeds,
        setpoint: ClassicalSetPoint,
        object_name: str,
    ):
        logger.info(f"sbc.env: {BLUER_SBC_ENV}")

        self.keyboard = keyboard
        self.leds = leds
        self.setpoint = setpoint

        self.object_name = object_name

    def initialize(self) -> bool:
        return camera.open(log=True)

    def cleanup(self):
        camera.close(log=True)

    def send_debug_data(self, data: Any) -> bool:
        socket = SocketComm.connect_to(DEV_HOST)
        return socket.send_data(data)

    # multi-threaded support
    def stop(self):
        pass

    def update(self) -> bool:
        return True
