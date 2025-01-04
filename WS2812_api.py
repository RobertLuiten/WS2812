import array, random
from machine import Pin
import rp2

class WS2812:
    
    """Implements the API for talking with the WS2812 RGB Light Strip."""
    
    def __init__(self, num_leds: int, pin_num: int, brightness: float =0.1, random_generator: Callable(int, int) = random.randint):
        """
        Initialize the light strip.

        Args:
        num_leds (int): The number of LEDs the light strip contains.
        pin_num (int): The pin number that the strip is connected to.
        brightness (float) (optional): Sets the initial brightness of the light strip for a value between 0 and 1 (Defaults to 0.1).
        random_generator (Callable(int, int)) (optional): The random number generator to use. Defaults to random.randint.
        
        """
        self.NUM_LEDS = num_leds
        self.PIN_NUM = pin_num
        self.RANDOM = random_generator
        self.brightness = brightness
        self.ar = array.array("I", [0 for _ in range(self.NUM_LEDS)])
        self.sm = self._init_state_machine()

    def _init_state_machine(self):
        """Initialize the state of the light strip."""
        @rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
        def ws2812():
            T1 = 2
            T2 = 5
            T3 = 3
            wrap_target()
            label("bitloop")
            out(x, 1)               .side(0) [T3 - 1]
            jmp(not_x, "do_zero")   .side(1) [T1 - 1]
            jmp("bitloop")          .side(1) [T2 - 1]
            label("do_zero")
            nop()                   .side(0) [T2 - 1]
            wrap()
        
        sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(self.PIN_NUM))
        sm.active(1)
        return sm

    def refresh(self):
        """Refreshes the current state of the light strip."""
        dimmer_ar = array.array("I", [0 for _ in range(self.NUM_LEDS)])
        for i, c in enumerate(self.ar):
            r = int(((c >> 8) & 0xFF) * self.brightness)
            g = int(((c >> 16) & 0xFF) * self.brightness)
            b = int((c & 0xFF) * self.brightness)
            dimmer_ar[i] = (g<<16) + (r<<8) + b
        self.sm.put(dimmer_ar, 8)
        
    def set_brightness(self, brightness: float):
        """
        Changes the brightness of the light strip.
        
        Args:
        brightness (float): A value between 0 and 1 representing the brightness of the light strip
        
        """
        self.brightness = brightness
        self.refresh()

    def set_pixel(self, i: int, color: (int, int, int)):
        """
        Sets a pixel to a color.
        
        Args:
        i (int): The number of the RGB to set.
        color ((int, int, int)): RGB value tuple to set the strip to.
        
        """
        self.ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]
        self.refresh()
        
    def set_pixel_off(self, i: int):
        """
        Turns a pixel off.
        
        Args:
        i (int): The pixel to turn off.
        
        """
        self.ar[i] = 0
        self.refresh()
        
    def set_pixel_random(self, i: int):
        """
        Sets a pixel to a random color.
        
        Args:
        i (int): The pixel to set randomly.
        
        """
        r = self.RANDOM(0, 255)
        g = self.RANDOM(0, 255)
        b = self.RANDOM(0, 255)
        self.set_pixel(i,(r, g, b))
        
    def set_all_same(self, color: (int, int, int)):
        """
        Sets all pixels to the same color.
        
        Args:
        color ((int, int, int)): RGB value tuple to set the strip to.
        
        """
        for i in range(len(self.ar)):
            self.set_pixel(i, color)
        
    def set_all_off(self):
        """Sets all lights in the strip to off."""
        self.set_all_same((0, 0, 0))
        self.refresh()
        
    def set_all_random(self):
        """
        Fills the strip with random colors.

        """
        for i in range(len(self.ar)):
            self.set_pixel_random(i)
            
    def set_section(self, colors: List[Union[Tuple[int, int, int], None]], index: int = 0):
        """
        Fills a section of the strip with given colors or random colors for None values.
        
        Args:
        colors (List[Union[Tuple[int, int, int], None]]): Array of colors to set the section to, with None values indicating random colors.
        index (int) (optional): Starting index of the section, zero-indexed. Defaults to 0.
        """
        for i, color in enumerate(colors):
            if color is None:
                self.set_pixel_random(index + i)
            else:
                self.set_pixel(index + i, color)
                
    def set_section_random(self, length: int, index: int = 0):
        """
        Fills a section of the strip with random colors
        
        Args:
        length (int): The length of the section to set to random colors.
        index (int) (optional): Starting index of the section, zero-indexed. Defaults to 0.
        
        """
        for i in range(length):
            self.set_pixel_random(index + i)
            
    def change_number_generator(random_generator: Callable(int, int)):
        """
        Changes the random number generator the api utilizes.
        
        Args:
        random_generator (Callable(int, int)): The random number generator to use.
        
        """
        self.RANDOM = random_generator