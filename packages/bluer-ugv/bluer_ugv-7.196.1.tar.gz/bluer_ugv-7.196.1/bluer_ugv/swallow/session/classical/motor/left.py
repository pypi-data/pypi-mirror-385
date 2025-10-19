from bluer_ugv.swallow.session.classical.leds import ClassicalLeds
from bluer_ugv.swallow.session.classical.motor.generic import GenericMotor
from bluer_ugv.swallow.session.classical.setpoint.classes import ClassicalSetPoint


class ClassicalLeftMotor(GenericMotor):
    def __init__(
        self,
        setpoint: ClassicalSetPoint,
        leds: ClassicalLeds,
    ):
        super().__init__(
            role="left",
            lpwm_pin=19,
            rpwm_pin=13,
            setpoint=setpoint,
            leds=leds,
        )
