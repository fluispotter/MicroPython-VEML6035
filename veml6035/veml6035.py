import time
from micropython import const

_COMMAND_REGISTER_CONFIGURATION = const(0)
_COMMAND_REGISTER_HIGH_THRESHOLD_SETTING = const(1)
_COMMAND_REGISTER_LOW_THRESHOLD_SETTING = const(2)
_COMMAND_REGISTER_POWER_SAFE_MODE = const(3)
_COMMAND_REGISTER_AMBIENT_LIGHT_DATA = const(4)
_COMMAND_REGISTER_WHITE_CHANNEL_DATA = const(5)
_COMMAND_REGISTER_INTERRUPT_STATUS = const(6)

CONFIGURATION_SENSITIVITY_HIGH = 0
CONFIGURATION_SENSITIVITY_LOW = 1
CONFIGURATION_DG_NORMAL = 0
CONFIGURATION_DG_DOUBLE = 1
CONFIGURATION_GAIN_NORMAL = 0
CONFIGURATION_GAIN_DOUBLE = 1
CONFIGURATION_INTEGRATION_TIME_25MS = 0b1100
CONFIGURATION_INTEGRATION_TIME_50MS = 0b1000
CONFIGURATION_INTEGRATION_TIME_100MS = 0b0000
CONFIGURATION_INTEGRATION_TIME_200MS = 0b0001
CONFIGURATION_INTEGRATION_TIME_400MS = 0b0010
CONFIGURATION_INTEGRATION_TIME_800MS = 0b0011
"""The VEML6035 is capable of a resolution of 0.0004 lux for dim light
sources in the range of approximately 0 to 26 lux. This can be achieved
by using:

| Configuration    | Value                                                                                             |
|------------------|---------------------------------------------------------------------------------------------------|
| Integration time | [CONFIGURATION_INTEGRATION_TIME_800MS][fluispotter.veml6035.CONFIGURATION_INTEGRATION_TIME_800MS] |
| Gain             | [CONFIGURATION_GAIN_DOUBLE][fluispotter.veml6035.CONFIGURATION_GAIN_DOUBLE]                       |
| DG               | [CONFIGURATION_DG_DOUBLE][fluispotter.veml6035.CONFIGURATION_DG_DOUBLE]                           |
| Sensitivity      | [CONFIGURATION_SENSITIVITY_HIGH][fluispotter.veml6035.CONFIGURATION_SENSITIVITY_HIGH]             |

For brighter light sources up to about 6710 lux gain, dg and sensitivity can be
reduced at the cost of the resolution. Higher integration time results in
a higher resolution but if faster meassurements are needed it can be reduced
down to 25 ms.

The following is the recommended starting point to avoid saturation / overflow effects.

| Configuration    | Value                                                                                             |
|------------------|---------------------------------------------------------------------------------------------------|
| Integration time | [CONFIGURATION_INTEGRATION_TIME_100MS][fluispotter.veml6035.CONFIGURATION_INTEGRATION_TIME_100MS] |
| Gain             | [CONFIGURATION_GAIN_NORMAL][fluispotter.veml6035.CONFIGURATION_GAIN_NORMAL]                       |
| DG               | [CONFIGURATION_DG_NORMAL][fluispotter.veml6035.CONFIGURATION_DG_NORMAL]                           |
| Sensitivity      | [CONFIGURATION_SENSITIVITY_LOW][fluispotter.veml6035.CONFIGURATION_SENSITIVITY_LOW]               |

To determine correct configuration values for the device start out with the above values
and read the raw light value. While the raw value is less than or equal to 100 keep increasing the
configuration values.

1. Increase sensitivity to [CONFIGURATION_SENSITIVITY_HIGH][fluispotter.veml6035.CONFIGURATION_SENSITIVITY_HIGH].
1. Increase gain to [CONFIGURATION_GAIN_DOUBLE][fluispotter.veml6035.CONFIGURATION_GAIN_DOUBLE].
1. Increase dg to [CONFIGURATION_DG_DOUBLE][fluispotter.veml6035.CONFIGURATION_DG_DOUBLE].
1. Increase integration time to [CONFIGURATION_INTEGRATION_TIME_200MS][fluispotter.veml6035.CONFIGURATION_INTEGRATION_TIME_200MS]
    and keep increasing integration time all the way up to [CONFIGURATION_INTEGRATION_TIME_800MS][fluispotter.veml6035.CONFIGURATION_INTEGRATION_TIME_800MS].
""" # noqa: E501
CONFIGURATION_PERSISTENCE_1 = 0b00
CONFIGURATION_PERSISTENCE_2 = 0b01
CONFIGURATION_PERSISTENCE_4 = 0b10
CONFIGURATION_PERSISTENCE_8 = 0b11
CONFIGURATION_INTERRUPT_CHANNEL_AMBIENT_LIGHT = 0
CONFIGURATION_INTERRUPT_CHANNEL_WHITE = 1
CONFIGURATION_CHANNEL_ENABLE_AMBIENT_LIGHT = 0
CONFIGURATION_CHANNEL_ENABLE_WHITE = 1
CONFIGURATION_INTERRUPT_DISABLE = 0
CONFIGURATION_INTERRUPT_ENABLE = 1
CONFIGURATION_SHUTDOWN_POWER_ON = 0
CONFIGURATION_SHUTDOWN_POWER_OFF = 1

POWER_SAFE_MODE_WAIT_400MS = 0b00
POWER_SAFE_MODE_WAIT_800MS = 0b01
POWER_SAFE_MODE_WAIT_1600MS = 0b10
POWER_SAFE_MODE_WAIT_3200MS = 0b11
POWER_SAFE_MODE_DISABLE = 0
POWER_SAFE_MODE_ENABLE = 1

_CONFIGURATION_INTEGRATION_TIME = {
    CONFIGURATION_INTEGRATION_TIME_25MS: 25,
    CONFIGURATION_INTEGRATION_TIME_50MS: 50,
    CONFIGURATION_INTEGRATION_TIME_100MS: 100,
    CONFIGURATION_INTEGRATION_TIME_200MS: 200,
    CONFIGURATION_INTEGRATION_TIME_400MS: 400,
    CONFIGURATION_INTEGRATION_TIME_800MS: 800
}

def lux_resolution(integration_time, gain, dg, sensitivity):
    # https://www.vishay.com/docs/84944/designingveml6035.pdf page 6.
    return (0.0004
        * (800 / _CONFIGURATION_INTEGRATION_TIME[integration_time])
        * (2 - dg)
        * (2 - gain)
        * (1 + 7 * sensitivity))

class VEML6035:
    _BUFFER_16 = bytearray(2)

    def __init__(self, i2c, address=0x29):
        self._i2c = i2c
        self._address = address

    def _read_u16(self, memaddr):
        self._i2c.readfrom_mem_into(self._address, memaddr, self._BUFFER_16)
        return (self._BUFFER_16[1] << 8) | self._BUFFER_16[0]

    def _write_u16(self, memaddr, val):
        self._BUFFER_16[0] = val & 0xFF
        self._BUFFER_16[1] = (val >> 8) & 0xFF
        self._i2c.writeto_mem(self._address, memaddr, self._BUFFER_16)

    def calibrate(self):
        # https://www.vishay.com/docs/84944/designingveml6035.pdf pages 14 and 20
        for integration_time, gain, dg, sensitivity in (
                (CONFIGURATION_INTEGRATION_TIME_100MS, CONFIGURATION_GAIN_NORMAL, CONFIGURATION_DG_NORMAL, CONFIGURATION_SENSITIVITY_LOW), # noqa: E501
                (CONFIGURATION_INTEGRATION_TIME_100MS, CONFIGURATION_GAIN_NORMAL, CONFIGURATION_DG_NORMAL, CONFIGURATION_SENSITIVITY_HIGH), # noqa: E501
                (CONFIGURATION_INTEGRATION_TIME_100MS, CONFIGURATION_GAIN_DOUBLE, CONFIGURATION_DG_NORMAL, CONFIGURATION_SENSITIVITY_HIGH), # noqa: E501
                (CONFIGURATION_INTEGRATION_TIME_100MS, CONFIGURATION_GAIN_DOUBLE, CONFIGURATION_DG_DOUBLE, CONFIGURATION_SENSITIVITY_HIGH), # noqa: E501
                (CONFIGURATION_INTEGRATION_TIME_200MS, CONFIGURATION_GAIN_DOUBLE, CONFIGURATION_DG_DOUBLE, CONFIGURATION_SENSITIVITY_HIGH), # noqa: E501
                (CONFIGURATION_INTEGRATION_TIME_400MS, CONFIGURATION_GAIN_DOUBLE, CONFIGURATION_DG_DOUBLE, CONFIGURATION_SENSITIVITY_HIGH), # noqa: E501
                (CONFIGURATION_INTEGRATION_TIME_800MS, CONFIGURATION_GAIN_DOUBLE, CONFIGURATION_DG_DOUBLE, CONFIGURATION_SENSITIVITY_HIGH)): # noqa: E501
            self.write_configuration(integration_time=integration_time, gain=gain, dg=dg, sensitivity=sensitivity)
            time.sleep_ms(max(int(_CONFIGURATION_INTEGRATION_TIME[integration_time] * 2), 500))
            data = self._read_u16(_COMMAND_REGISTER_AMBIENT_LIGHT_DATA)

            if data > 100:
                break

    def read_configuration(self):
        conf = self._read_u16(_COMMAND_REGISTER_CONFIGURATION)

        shutdown = conf & 0x01
        interrupt_enable = (conf >> 1) & 0x01
        channel_enable = (conf >> 2) & 0x01
        interrupt_channel = (conf >> 3) & 0x01
        persistence = (conf >> 4) & 0x03
        integration_time = (conf >> 6) & 0x0F
        gain = (conf >> 10) & 0x01
        dg = (conf >> 11) & 0x01
        sensitivity = (conf >> 12) & 0x01

        return (shutdown,
            interrupt_enable,
            channel_enable,
            interrupt_channel,
            persistence,
            integration_time,
            gain,
            dg,
            sensitivity)

    def write_configuration(self,
            shutdown=CONFIGURATION_SHUTDOWN_POWER_ON,
            interrupt_enable=CONFIGURATION_INTERRUPT_DISABLE,
            channel_enable=CONFIGURATION_CHANNEL_ENABLE_AMBIENT_LIGHT,
            interrupt_channel=CONFIGURATION_INTERRUPT_CHANNEL_AMBIENT_LIGHT,
            persistence=CONFIGURATION_PERSISTENCE_1,
            integration_time=CONFIGURATION_INTEGRATION_TIME_100MS,
            gain=CONFIGURATION_GAIN_NORMAL,
            dg=CONFIGURATION_DG_NORMAL,
            sensitivity=CONFIGURATION_SENSITIVITY_LOW):
        conf = (
            shutdown
            | (interrupt_enable << 1)
            | (channel_enable << 2)
            | (interrupt_channel << 3)
            | (persistence << 4)
            | (integration_time << 6)
            | (gain << 10)
            | (dg << 11)
            | (sensitivity << 12))
        self._write_u16(_COMMAND_REGISTER_CONFIGURATION, conf)

    def read_ambient_light(self):
        data = self._read_u16(_COMMAND_REGISTER_AMBIENT_LIGHT_DATA)
        *_, integration_time, gain, dg, sensitivity = self.read_configuration()
        resolution = lux_resolution(integration_time, gain, dg, sensitivity)
        return data * resolution
