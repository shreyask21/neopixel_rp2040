# Experimental Neopixel (WS2812B) Micropython Library for Raspberry Pi Pico/RP2040
# Using PIO Finite State Machines
# Author: ShreyasK (https://github.com/shreyask21)

import array, time
from machine import Pin
from rp2 import PIO, StateMachine, asm_pio

class neopixel:
    ########### Variables ###########
    numLED = 1 # Number of LEDs in series
    dataPin = 22 # DIN Pin on RP2040
    
    
    def RGB(R,G,B):
        return int(R<<16 | G <<8 | B)
        
    # Color definitions
    BLACK = RGB(0,0,0)       
    WHITE = RGB(255,255,255)       
    RED = RGB(255,0,0)       
    GREEN = RGB(0,255,0)       
    BLUE =  RGB(0,0,255)       
    YELLOW = RGB(255,255,0)       
    MAGENTA = RGB(255,0,255)       
    CYAN = RGB(0,255,255)
    COLORS = [BLACK, RED, GREEN, BLUE, CYAN, MAGENTA, YELLOW, WHITE]
    
    # Placeholders
    dataArray = None
    stateMachine = None
    brightnessOffset = 1
    ########### Functions ###########
    # State Machine Assembly for sending the bitstream to LEDs
    @asm_pio(sideset_init=PIO.OUT_LOW, out_shiftdir=PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
    def driver():
        T1 = 2
        T2 = 5
        T3 = 3
        label("bitloop")
        out(x, 1) .side(0) [T3 - 1]
        jmp(not_x, "do_zero") .side(1) [T1 - 1]
        jmp("bitloop") .side(1) [T2 - 1]
        label("do_zero")
        nop() .side(0) [T2 - 1]
        
    # Constructor
    def __init__(self, LEDS=1, PIN=22):
        self.numLED = LEDS
        self.dataPin = PIN
        # Create the State Machine with the driver program.
        self.stateMachine = StateMachine(0, self.driver, freq=8000000, sideset_base=Pin(self.dataPin))
        # Start the StateMachine
        self.stateMachine.active(1)
        # Create data buffer for holding RGB Values
        self.dataArray = array.array("I", [0 for _ in range(self.numLED)])
        
    
    # Set single or all LEDs
    def set(self, LED_NUMBER=None, R=0xFF, G=0xFF, B=0xFF, COLOR=None, brightness=1):
            self.brightnessOffset = brightness
            if(LED_NUMBER==None):
                if(COLOR==None):
                    for LED_NUMBER in range(self.numLED):
                        self.dataArray[LED_NUMBER] = int(self.brightnessOffset * (R<<8 | G <<16 | B))
                else:
                    for LED_NUMBER in range(self.numLED):
                        self.dataArray[LED_NUMBER] = int(self.brightnessOffset *(((COLOR&0xFF0000)>>8) | ((COLOR&0xFF00)<<8) | ((COLOR&0xFF))))
            else:
                if(COLOR==None):
                    self.dataArray[LED_NUMBER] = int(self.brightnessOffset * (R<<8 | G <<16 | B))
                else:
                    self.dataArray[LED_NUMBER] = int(self.brightnessOffset * (((COLOR&0xFF0000)>>8) | ((COLOR&0xFF00)<<8) | ((COLOR&0xFF))))
            self.stateMachine.put(self.dataArray,8)
                
    # Reset Given or All LED 
    def reset(self, LED_NUMBER=None):
        if(LED_NUMBER==None):
            for LED_NUMBER in range(self.numLED):
                self.dataArray[LED_NUMBER] = 0
            self.stateMachine.put(self.dataArray,8)
        else:
            self.dataArray[LED_NUMBER] = 0
            self.stateMachine.put(self.dataArray,8)

    # Change Brightness of Single or All LEDs          
    def setBrightness(self, LED_NUMBER=None, brightness=1):
        self.brightnessOffset = brightness
        if(LED_NUMBER==None):
            for LED_NUMBER in range(self.numLED):
                    self.dataArray[LED_NUMBER] = int(brightness * self.dataArray[LED_NUMBER])
        else:
             self.dataArray[LED_NUMBER] = int(brightness * self.dataArray[LED_NUMBER])
        self.stateMachine.put(self.dataArray,8)
                
    # For testing individual LEDs
    def test(self):
        for j in range(0,self.numLED):
            for i in range(0,len(self.COLORS)):
                self.setLED(LED_NUMBER=j, COLOR=self.COLORS[i])
                time.sleep_ms(500)
            self.resetALL()
