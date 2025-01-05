import array, random, rp2
from machine import Pin

class WS2812:
    
    """MicroPython Controller for talking with the WS2812 RGB Light Strip."""
    
    def __init__(self, num_leds: int, pin_num: int, brightness: float = 0.1, random_generator: Callable(int, int) = random.randint):
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
        self.BRIGHTNESS = array.array("d", [brightness for _ in range(self.NUM_LEDS)])
        self.AR = array.array("I", [0 for _ in range(self.NUM_LEDS)])
        self.SM = self._init_state_machine()

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
        
        SM = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(self.PIN_NUM))
        SM.active(1)
        return SM

    def update(self):
        """Updates the current state of the light strip."""
        dimmer_ar = array.array("I", [0 for _ in range(self.NUM_LEDS)])
        for i, c in enumerate(self.AR):
            r = int(((c >> 8) & 0xFF) * self.BRIGHTNESS[i])
            g = int(((c >> 16) & 0xFF) * self.BRIGHTNESS[i])
            b = int((c & 0xFF) * self.BRIGHTNESS[i])
            dimmer_ar[i] = (g<<16) + (r<<8) + b
        self.SM.put(dimmer_ar, 8)

    def set_pixel_color(self, i: int, color: (int, int, int)):
        """
        Sets a pixel to a color.
        
        Args:
        i (int): The number of the RGB to set.
        color ((int, int, int)): RGB value tuple to set the strip to.
        
        """
        self.AR[i] = (color[1]<<16) + (color[0]<<8) + color[2]
        
    def set_pixel_off(self, i: int):
        """
        Turns a pixel off.
        
        Args:
        i (int): The pixel to turn off.
        
        """
        self.set_pixel_color(i, (0,0,0))
        
    def set_pixel_brightness(self, i: int, brightness: float):
        """
        Changes the brightness of the ith pixel.
        
        Args:
        i (int): The pixel to change the brightness of.
        brightness (float): A value between 0 and 1 representing the new bightness for the pixel.
        
        """
        self.BRIGHTNESS[i] = brightness
        
    def set_pixel_brightness_random(self, i: int, minB: float = 0, maxB: float = 1):
        """
        Sets a pixel to a random brightness.
        
        Args:
        i (int): The pixel to set randomly.
        minB (float) (optional): The minimum brightness to set the light to. Defaults to 0.
        maxB (float) (optional): The maximum brightness to set the light to. Defaults to 1.
        
        """
        self.BRIGHTNESS[i] = self.RANDOM(minB * 100, MaxB * 100) * 0.1
        
    def set_pixel_random(self, i: int):
        """
        Sets a pixel to a random color.
        
        Args:
        i (int): The pixel to set randomly.
        
        """
        r = self.RANDOM(0, 255)
        g = self.RANDOM(0, 255)
        b = self.RANDOM(0, 255)
        self.set_pixel_color(i,(r, g, b))
        
    def set_all(self, color: (int, int, int)):
        """
        Sets all pixels to the same color.
        
        Args:
        color ((int, int, int)): RGB value tuple to set the strip to.
        
        """
        for i in range(len(self.AR)):
            self.set_pixel_color(i, color)
        
    def set_all_off(self):
        """Sets all lights in the strip to off."""
        self.set_all((0, 0, 0))
        
    def set_all_brightness(self, brightness: float):
        """
        Changes the brightness of the light strip.
        
        Args:
        brightness (float): A value between 0 and 1 representing the new bightness for the lightstrip.
        
        """
        for i in range(len(self.BRIGHTNESS)):
            self.BRIGHTNESS[i] = brightness
            
    def set_all_brightness_random(self, minB: float = 0, maxB: float = 1):
        """
        Sets all pixels in the light strip to random brightness.
        
        Args:
        minB (float) (optional): The minimum brightness to set the light to. Defaults to 0.
        maxB (float) (optional): The maximum brightness to set the light to. Defaults to 1.
        
        """
        for i in range(len(self.BRIGHTNESS)):
            self.set_pixel_brightness_random(i, minB, maxB)
            
    def set_all_brightness_random_solid(self, minB: float = 0, maxB: float = 1):
        """Sets the light strip to a uniform random brightness.
        
        Args:
        minB (float) (optional): The minimum brightness to set the light to. Defaults to 0.
        maxB (float) (optional): The maximum brightness to set the light to. Defaults to 1.
        
        """
        rand_bright = self.RANDOM(minB, Maxb) * 0.1
        for i in range(len(self.BRIGHTNESS)):
            self.BRIGHTNESS[i] = rand_bright
        
    def set_all_random(self):
        """
        Fills the strip with random colors.

        """
        for i in range(len(self.AR)):
            self.set_pixel_random(i)
            
    def set_all_random_solid(self):
        """Sets all pixels to the same random color."""
        r = self.RANDOM(0, 255)
        g = self.RANDOM(0, 255)
        b = self.RANDOM(0, 255)
        self.set_all((r,g,b))
            
    def set_section(self, colors: List[[(int, int, int), None]], index: int = 0):
        """
        Fills a section of the strip with given colors or random colors for None values.
        
        Args:
        colors (List[(int, int, int)], None]]): Array of colors to set the section to, with None values indicating random colors.
        index (int) (optional): Starting index of the section, zero-indexed. Defaults to 0.
        """
        for i, color in enumerate(colors):
            if color is None:
                self.set_pixel_random(index + i)
            else:
                self.set_pixel_color(index + i, color)
                
    def set_section_off(self, length: int, index: int = 0):
        """
        Turns off a section of the strip.
        
        Args:
        length (int): The length of the section.
        index (int) (optional): Starting index of the section, zero-indexed. Defaults to 0.
        
        """
        for i in range(length):
            self.set_pixel_off(index + i)
                
    def set_section_solid(self, color: (int, int, int), length: int, index: int = 0):
        """
        Fills a section of the strip with random colors.
        
        Args:
        color ((int, int, int)): The color to set the section to.
        length (int): The length of the section.
        index (int) (optional): Starting index of the section, zero-indexed. Defaults to 0.
        
        """
        for i in range(length):
            self.set_pixel_color(index + i, color)
            
    def set_section_brightness(self, brightness: float, length: int, index: int = 0):
        """
        Sets the brightness for a section of the strip.
        
        Args:
        brightness (float): The brightness to set the section to.
        length (int): The length of the section.
        index (int) (optional): Starting index of the section, zero-indexed. Defaults to 0.
        
        """
        for i in range(length):
            self.set_pixel_brightness(index + i, brightness)
            
    def set_section_brightness_random(self, length: int, index: int = 0, minB: float = 0, maxB: float = 1):
        """
        Randomly sets the brightness for pixels in a section.
        
        Args:
        length (int): The length of the section.
        index (int) (optional): Starting index of the section, zero-indexed. Defaults to 0.
        minB (float) (optional): The minimum brightness to set the light to. Defaults to 0.
        maxB (float) (optional): The maximum brightness to set the light to. Defaults to 1.
        
        """
        for i in range(length):
            self.set_pixel_brightness_random(i, minB, maxB)
            
    def set_section_brightness_random_solid(self, length: int, index: int = 0, minB: float = 0, maxB: float = 1):
        """
        Randomly sets the for pixels in a section to a uniform brightness.
        
        Args:
        length (int): The length of the section.
        index (int) (optional): Starting index of the section, zero-indexed. Defaults to 0.
        minB (float) (optional): The minimum brightness to set the light to. Defaults to 0.
        maxB (float) (optional): The maximum brightness to set the light to. Defaults to 1.
        
        """
        rand_bright = self.RANDOM(minB * 100, maxB * 100) * 0.1
        for i in range(length):
            self.set_pixel_brightness(i, rand_bright)
                
    def set_section_random(self, length: int, index: int = 0):
        """
        Fills a section of the strip with random colors.
        
        Args:
        length (int): The length of the section.
        index (int) (optional): Starting index of the section, zero-indexed. Defaults to 0.
        
        """
        for i in range(length):
            self.set_pixel_random(index + i)
            
    def set_section_random_solid(self, length: int, index: int = 0):
        """
        Sets a section to a solid random color.
        
        Args:
        length (int): The length of the section.
        index (int) (optional): Starting index of the section, zero-indexed. Defaults to 0.
        
        """
        r = self.RANDOM(0, 255)
        g = self.RANDOM(0, 255)
        b = self.RANDOM(0, 255)
        set_section_solid((r,g,b),length, int)
        
    def get_pixel_color(self, i: int) -> (int, int, int):
        """
        Retrieves the color of a pixel.
        
        Args:
        i (int): The number of the RGB to get the color from.
        
        Returns:
        (int, int, int): (R,G,B) color representation
        
        """
        color = self.AR[i]
        r : int = ((color >> 8) & 0xFF)
        g : int = ((color >> 16) & 0xFF)
        b : int = (color & 0xFF)
        return (r,g,b)
    
    def pixel_on(self, i: int) -> bool:
        """
        Determines whether a pixel is on or not.
        
        Args:
        i (int): The pixel to check.
        
        Returns:
        (bool): True if the pixel is off, false otherwise.
        
        """
        return (self.get_pixel_color(i) != (0,0,0)) and self.get_pixel_brightness != 0
    
    def get_pixel_brightness(self, i: int) -> float:
        """
        Retrieves the brightness of a pixel.
        
        Args:
        i (int): The number of the RGB to get the brightness from.
        
        Returns:
        float: A value between 0 and 1 representing the pixel's brightness
        
        """
        return self.BRIGHTNESS[i]
    
    def change_number_generator(random_generator: Callable(int, int)):
        """
        Changes the random number generator the controller utilizes.
        
        Args:
        random_generator (Callable(int, int)): The random number generator to use.
        
        """
        self.RANDOM = random_generatori
