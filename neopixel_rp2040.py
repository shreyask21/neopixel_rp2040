# Experimental Neopixel (WS2812B) Micropython Library for Raspberry Pi Pico/RP2040
# Using PIO Finite State Machines
# Author: ShreyasK (https://github.com/shreyask21)

import array
import time
from machine import Pin
from rp2 import PIO, StateMachine, asm_pio


class neopixel:
    """
    Neopixel driver class

    ...

    Attributes
    ----------
    BLACK, RED, GREEN, BLUE, CYAN, MAGENTA, YELLOW, WHITE : int,
        24bit color value definations

    COLORS : int [],
        Above 24Bit colors in Array format

    Methods
    -------
    RGB(R: int, G: int, B: int) -> int:,
        Get Combined 24Bit RGB Value

    set(self, LED_NUMBER=None, START_LED=None, STOP_LED=None, R=0xFF, G=0xFF, B=0xFF, COLOR=None, BRIGHTNESS=1):,
        Sets color for single, multiple or all LEDs

    reset(self, LED_NUMBER=None, START_LED=None, STOP_LED=None):,
        Resets single, multiple or all LEDs

    setBrightness(self, LED_NUMBER=None, BRIGHTNESS=0.5,  START_LED=None, STOP_LED=None):,
        Changes brightness of single, multiple or all LEDs

    test(self):,
        Tests All Connected LEDs, one at a time. Useful for debugging circuit faults.
    """
    __numLED = 1  # Number of LEDs in series
    __dataPin = 22  # DIN Pin on RP2040

    def RGB(R: int, G: int, B: int) -> int:
        """ Get Combined 24Bit RGB Value

        Parameters
        ----------
        R,G,B : int,
            individual RGB color values
        """
        return int(R << 16 | G << 8 | B)

    # Color definitions
    BLACK = RGB(0, 0, 0)
    WHITE = RGB(255, 255, 255)
    RED = RGB(255, 0, 0)
    GREEN = RGB(0, 255, 0)
    BLUE = RGB(0, 0, 255)
    YELLOW = RGB(255, 255, 0)
    MAGENTA = RGB(255, 0, 255)
    CYAN = RGB(0, 255, 255)
    COLORS = [BLACK, RED, GREEN, BLUE, CYAN, MAGENTA, YELLOW, WHITE]

    __bitstreamArray = None
    __stateMachine = None
    __brightnessOffset = float(1.0)
    __rawColor = None

    @asm_pio(sideset_init=PIO.OUT_LOW, out_shiftdir=PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
    def __driver__():
        """
        State Machine Assembly for sending the bitstream to LEDs.
        Internal class function, not intended for external calling.

        """
        T1 = 2
        T2 = 5
        T3 = 3
        label("bitloop")
        out(x, 1) .side(0)[T3 - 1]
        jmp(not_x, "do_zero") .side(1)[T1 - 1]
        jmp("bitloop") .side(1)[T2 - 1]
        label("do_zero")
        nop() .side(0)[T2 - 1]

    def __init__(self, LEDS: int = 1, PIN: int = 22):
        """
        Parameters
        ----------
        LEDS : int,
            Number of LEDs connected  

        PIN : int, 
            The pin on RP2040 used to connect to DIN of LED

        """
        self.__numLED = LEDS
        self.__dataPin = PIN
        # Create the State Machine with the pin driving assembly program.
        self.__stateMachine = StateMachine(
            0, self.__driver__, freq=8000000, sideset_base=Pin(self.__dataPin))
        # Start the __stateMachine
        self.__stateMachine.active(1)
        # Create data buffer for holding RGB Values
        self.__bitstreamArray = array.array(
            "I", [0 for _ in range(self.__numLED)])
        self.reset()

    def set(self, LED_NUMBER: int = None, START_LED: int = None, STOP_LED: int = None, R: int = 0xFF, G: int = 0xFF, B: int = 0xFF, COLOR: int = None, BRIGHTNESS: float = 1):
        """ Sets color for single, multiple or all LEDs

        If no argument is passed, all connected LED will be turned on with white color by default.

        Parameters
        ----------
        LED_NUMBER : int, optional  
            The number of LED to modify (default is None) 

        START_LED, STOP_LED : int, optional  
            The Range of LEDs to modify colors  

        R, G, B : int (0-255), optional  
            Individual color values to use  

        COLOR : int (0-16.7M), optional  
            24bit color value to use  

        BRIGHTNESS: float (0.0-1), optional  
            The brightness modifier  

        Note
        ------
            If both R,G,B and COLOR parameters are provided, the COLOR parameter is assumed to be dominant.
        """
        self.__brightnessOffset = BRIGHTNESS
        if(COLOR == None):
            COLOR = int(G << 16 | R << 8 | B)

        red = int(((COLOR >> 8) & 0xFF) * BRIGHTNESS)
        green = int(((COLOR >> 16) & 0xFF) * BRIGHTNESS)
        blue = int((COLOR & 0xFF) * BRIGHTNESS)

        RGB_SAMPLE = ((green << 16) + (red << 8) + blue)

        if(START_LED == None and STOP_LED == None):
            if(LED_NUMBER == None):
                for LED_NUMBER in range(self.__numLED):
                    self.__bitstreamArray[LED_NUMBER] = RGB_SAMPLE
            else:
                self.__bitstreamArray[LED_NUMBER] = RGB_SAMPLE
        else:
            for i in range(START_LED, STOP_LED+1):
                self.__bitstreamArray[i] = RGB_SAMPLE

        self.__stateMachine.put(self.__bitstreamArray, 8)

    def reset(self, LED_NUMBER: int = None, START_LED: int = None, STOP_LED: int = None):
        """ Resets single, multiple or all LEDs

        If no argument is passed, all connected LED will be reset (Turned off).

        Parameters
        ----------
        LED_NUMBER : int, optional
            The number of LED to modify (default is None)

        START_LED, STOP_LED : int, optional
            The Range of LEDs to modify
        """
        if(START_LED == None and STOP_LED == None):
            if(LED_NUMBER == None):
                for LED_NUMBER in range(self.__numLED):
                    self.__bitstreamArray[LED_NUMBER] = 0
                self.__stateMachine.put(self.__bitstreamArray, 8)
            else:
                self.__bitstreamArray[LED_NUMBER] = 0
                self.__stateMachine.put(self.__bitstreamArray, 8)
        else:
            for i in range(START_LED, STOP_LED+1):
                self.__bitstreamArray[i] = int(0)

    # TODO: RGB-> HSL conversion for brightness manipulation
    def setBrightness(self, LED_NUMBER: int = None, BRIGHTNESS: int = 0.5,  START_LED: int = None, STOP_LED: int = None):
        """ Changes brightness of single, multiple or all LEDs

        If no argument is passed, all connected LED will modified.

        Parameters
        ----------
        LED_NUMBER : int, optional
            The number of LED to modify (default is None)

        START_LED, STOP_LED : int, optional
            The Range of LEDs to modify

        BRIGHTNESS: float (0.0-1), optional  
            The brightness modifier
        """
        self.__brightnessOffset = BRIGHTNESS
        if(START_LED == None and STOP_LED == None):
            if(LED_NUMBER == None):
                for LED_NUMBER in range(self.__numLED):
                    self.__bitstreamArray[LED_NUMBER] = int(
                        BRIGHTNESS * self.__bitstreamArray[LED_NUMBER])
            else:
                self.__bitstreamArray[LED_NUMBER] = int(
                    BRIGHTNESS * self.__bitstreamArray[LED_NUMBER])
        else:
            for i in range(START_LED, STOP_LED+1):
                self.__bitstreamArray[i] = int(
                    BRIGHTNESS * self.__bitstreamArray[i])

        self.__stateMachine.put(self.__bitstreamArray, 8)

    def test(self):
        """ Tests All Connected LEDs, one at a time.
            Useful for debugging circuit faults.

        Parameters
        ----------
        None
        """
        for j in range(0, self.__numLED):
            for i in range(0, len(self.COLORS)):
                self.set(LED_NUMBER=j, COLOR=self.COLORS[i])
                time.sleep_ms(500)
            self.reset()
