from .racecar import Racecar
import traitlets
from adafruit_servokit import ServoKit


class NvidiaRacecar(Racecar):
    
    i2c_address1 = traitlets.Integer(default_value=0x40)
    i2c_address2 = traitlets.Integer(default_value=0x60)
    steering_gain = traitlets.Float(default_value=-0.65)
    steering_offset = traitlets.Float(default_value=0)
    steering_channel = traitlets.Integer(default_value=0)
    throttle_gain = traitlets.Float(default_value=0.8)
    
    def __init__(self, *args, **kwargs):
        super(NvidiaRacecar, self).__init__(*args, **kwargs)
        self.kit = ServoKit(channels=16, address=self.i2c_address1)
        self.motor = ServoKit(channels=16, address=self.i2c_address2)
        self.motor._pca.frequency = 1600
        self.steering_motor = self.kit.continuous_servo[self.steering_channel]
    
    @traitlets.observe('steering')
    def _on_steering(self, change):
        self.steering_motor.throttle = change['new'] * self.steering_gain + self.steering_offset
    
    @traitlets.observe('throttle')
    def _on_throttle(self, change):
        if change['new'] > 0:
            self.motor._pca.channels[0].duty_cycle = int(0xFFFF * (change['new'] * self.throttle_gain))
            self.motor._pca.channels[1].duty_cycle = 0xFFFF
            self.motor._pca.channels[2].duty_cycle = 0
            self.motor._pca.channels[3].duty_cycle = 0
            self.motor._pca.channels[4].duty_cycle = int(0xFFFF * (change['new'] * self.throttle_gain))
            self.motor._pca.channels[7].duty_cycle = int(0xFFFF * (change['new'] * self.throttle_gain))
            self.motor._pca.channels[6].duty_cycle = 0xFFFF
            self.motor._pca.channels[5].duty_cycle = 0
        else:
            self.motor._pca.channels[0].duty_cycle = int(-0xFFFF * (change['new'] * self.throttle_gain))
            self.motor._pca.channels[1].duty_cycle = 0
            self.motor._pca.channels[2].duty_cycle = 0xFFFF
            self.motor._pca.channels[3].duty_cycle = int(-0xFFFF * (change['new'] * self.throttle_gain))
            self.motor._pca.channels[4].duty_cycle = 0
            self.motor._pca.channels[7].duty_cycle = int(-0xFFFF * (change['new'] * self.throttle_gain))
            self.motor._pca.channels[6].duty_cycle = 0
            self.motor._pca.channels[5].duty_cycle = 0xFFFF
