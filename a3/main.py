from machine import Pin, ADC, PWM
from time import sleep

pin_led = Pin("LED", Pin.OUT)

# servo pin setup
# https://osoyoo.com/2021/07/20/raspberry-pi-pico-learning-kit-lesson-5-use-potentiometer-to-control-servo/
# https://randomnerdtutorials.com/raspberry-pi-pico-servo-motor-micropython/
pin_servo = PWM(Pin(16))
min_duty = 7864
max_duty = 1802
freq = 50
pin_servo.duty_u16(min_duty) # starting position
pin_servo.freq(freq)

# rain sensor setup
# https://how2electronics.com/flood-monitoring-with-raindrop-sensor-raspberry-pi-pico/
pin_rain = ADC(0)
is_raining = None # since errors set it to None

# Rain sensor watchdog & fail safe mode setup
sensor_watchdog = 0 # number of reading failures
allowed_fails = 3
run_failsafe = False

def servo_wave(speed: float):
    """
    Waves the wiper arm back and forth once.
    
    Args:
        speed (float): time time for the servo to complete the wiping movement
    """
    pin_servo.duty_u16(min_duty)
    sleep(speed/2)
    pin_servo.duty_u16(max_duty)
    sleep(speed/2)
    
def rain_read() -> bool:
    """
    Reads the rain sensor value
    
    Returns:
        boolean: There's rain on the detector surface (True/False)
        None: An error has occured.
    """
    try:
        raw_read = pin_rain.read_u16()
        print("\t\tRain sensor raw_read: ", raw_read)
    except (OSError, TypeError) as e:
        print("\t- Rain sensor reading failed:", e)
        return None
    if raw_read < 1500:
        print("\t- Rain sensor disconnected.")
        return None
    elif raw_read > 60000:
        print("\t- Rain sensor most likely broken.")
        return None
    return raw_read < 4000

# Startup blinking
pin_led.on()
sleep(1)
pin_led.off()
sleep(1)

try:
    while True:
        is_raining = rain_read() # update is_raining

        # The system has just received an invalid reading
        if is_raining is None:
            sensor_watchdog += 1
            
            # Rain sensor has failed, and the issue is known by the system
            if run_failsafe is True and is_raining is None:
                servo_wave(3.0)
                print(f"WARNING: Running in failsafe mode due to {sensor_watchdog} failed readings from rain sensor. Please check the connections, and replace the component if necessary.")
            
            # Error has just appeared
            elif sensor_watchdog >= allowed_fails:
                print("WARNING: Rain sensor reading error detected. Entering FAILSAFE mode.")
                run_failsafe = True
        
        
        # The system has received is_raining (True/False)
        else:
            sensor_watchdog = 0
            
            if is_raining:
                print("Raindrops detected.")
                for i in range(3): servo_wave(1.5)
            else:
                print("No raindrops detected.")
                pin_led.on()
                sleep(0.5)
                pin_led.off()
                sleep(1.5)
        
finally:
        print("Program ended")
        pin_servo.deinit()
        pin_led.off()
