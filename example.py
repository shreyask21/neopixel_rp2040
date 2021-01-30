import utime

''' Import Driver Library '''
import neopixel_rp2040


'''
    Create Object
    Here 'LEDS=' sets the number of LEDs connected in Neopixel string
         'PIN=' is the Pin number used to connect the DIN pin of the Neopixel to the Raspberry Pi Pico
'''
led = neopixel_rp2040.neopixel(LEDS=2, PIN=22)

'''
    Test All Connected LEDs
'''
led.test()
utime.sleep(2)

'''
    Set Single LED to green color with 50% brightness
'''
led.set(LED_NUMBER=0, COLOR=led.GREEN, BRIGHTNESS=0.5)
utime.sleep(2)

'''
    Reset Single LED
'''
led.reset(LED_NUMBER=0)
utime.sleep(2)

'''
    Turn On All LEDS to White
'''
led.set()
utime.sleep(2)

'''
    Reset All LEDs
'''
led.reset()
utime.sleep(2)

'''
   Change Brightness of single LED
'''
led.set(LED_NUMBER=0)
led.setBrightness(LED_NUMBER=0, BRIGHTNESS=0.5)
utime.sleep(2)
