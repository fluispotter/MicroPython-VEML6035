# MicroPython VEML6035

MicroPython driver for the [VEML6035](https://www.vishay.com/en/product/84889) ambient light sensor.

## Usage

The `VEML6035` constructor accepts an I2C instance.

```python
import time
from machine import Pin, I2C
from veml6035 import (
    VEML6035,
    CONFIGURATION_SHUTDOWN_POWER_ON,
    CONFIGURATION_INTEGRATION_TIME_25MS,
    CONFIGURATION_GAIN_NORMAL,
    CONFIGURATION_DG_NORMAL,
    CONFIGURATION_SENSITIVITY_HIGH)

i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=100000)

veml = VEML6035(i2c)

# Update configuration options and power on the sensor.
veml.write_configuration(
    shutdown=CONFIGURATION_SHUTDOWN_POWER_ON,
    integration_time=CONFIGURATION_INTEGRATION_TIME_25MS,
    gain=CONFIGURATION_GAIN_NORMAL,
    dg=CONFIGURATION_DG_NORMAL,
    sensitivity=CONFIGURATION_SENSITIVITY_HIGH)

# Get current configuration.
veml.read_configuration()

# Get current lux level reading.
veml.read_ambient_light()

# Calibrate sensor by following steps outlined in the datasheet.
veml.calibrate()
```
