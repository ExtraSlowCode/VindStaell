from machine import Pin, ADC, PWM
from time import sleep

pin_led = Pin("LED", Pin.OUT)

#servo pin setup
#https://osoyoo.com/2021/07/20/raspberry-pi-pico-learning-kit-lesson-5-use-potentiometer-to-control-servo/
#https://randomnerdtutorials.com/raspberry-pi-pico-servo-motor-micropython/
pin_servo = PWM(Pin(16))
max_duty = 7864 # 0deg
min_duty = 1802 # 180deg
freq = 50
pin_servo.duty_u16(min_duty) # avoid kickbacks?
pin_servo.freq(freq)

#rain sensor setup
#https://how2electronics.com/flood-monitoring-with-raindrop-sensor-raspberry-pi-pico/
pin_rain = ADC(0)
rain_read_max = 53200
rain_current = 0.0

def servo_wave(speed):
    pin_servo.duty_u16(min_duty)
    sleep(speed)
    pin_servo.duty_u16(max_duty)
    sleep(speed)
    
def rain_read():
    global rain_read_max
    amnt = pin_rain.read_u16()
    if amnt >= rain_read_max:
        rain_read_max = amnt
        print("RECORD READING!: ", amnt)
    else: 
        print("Read: ", amnt)
    rain_percent = (1-(amnt/rain_read_max)) * 100
    return rain_percent

pin_led.on()
sleep(1)
pin_led.off()
sleep(1)

try:
    while True:
        rain_current = rain_read()
        
        if rain_current > 90:
            servo_wave(0.5)
        elif rain_current > 40:
            servo_wave(1.0)
        else:
            pin_led.on()
            sleep(1.0)
            pin_led.off()
            sleep(2.0)
        print("Rain index %: ", rain_read())
        
finally:
        print("Program ended")
        pin_servo.deinit()
        pin_led.off()
