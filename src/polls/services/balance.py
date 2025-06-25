import platform
import time

from logger import logger

OFFSET = 295700
DOUT_PIN = 5
SCK_PIN = 6


def read_balance() -> float:
    """
    Performs 10 measurements and returns the average value, using a fixed offset.
    """
    if platform.machine() != "armv7l":
        logger.error("This function is only supported on Raspberry Pi devices.")
        return 0.0

    import RPi.GPIO as GPIO
    from hx711 import HX711

    GPIO.setmode(GPIO.BCM)
    try:
        hx = HX711(dout_pin=DOUT_PIN, pd_sck_pin=SCK_PIN)
        hx.set_debug_mode(True)
        logger.debug(f"Fixed offset used: {OFFSET}")

        measurements = []
        for i in range(10):
            measured_weight = hx.get_weight_mean(10) - OFFSET
            if measured_weight:
                logger.debug(f"Measurement {i + 1}: {measured_weight:.2f}g")
                measurements.append(measured_weight)
            else:
                logger.error(f"Error in measurement {i + 1}!")
            time.sleep(1)

        if measurements:
            average = sum(measurements) / len(measurements)
            logger.info(f"Average of measurements: {average:.2f}g")
            return average
        else:
            logger.error("No valid measurements taken!")
            return 0.0

    except Exception as e:
        logger.error(f"Error: {e}")
        return 0.0

    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    pass
