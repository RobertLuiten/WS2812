# WS2812 MicroPython Controller For Raspberry Pi Pico
Do you like lights? Do you like flashing colors? Computer? Then this WS2812 LEDs and this controller are for you! This MicroPython controller has several features:
- Low-level pixel by pixel brightness and color control.
- Macro brightness and color control.
- Built-in randomization support.
- Color and brightness retrieval.

In order to use this controller, you will need a WS2812 light strip and a Raspberry Pi Pico with Micropython installed. For more information on installing MicroPython, you can refer to [this Raspberry Pi documentation](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html).

# Initialization
To begin, add the ```WS2812_controller.py``` controller into your project along with connecting the light strip to a GP pin on your Raspberry Pi.

From here, you can import ```WS2812``` at the header of your Python file:
```
from WS2812_controller import WS2812
```
After connecting your light strip to the Pico, initilization is relatively simple. You can add a new light strip by the following:
```
example_strip_1 = WS2812(num_leds=8, pin_num=22) # Adding 8 LED long light strip in pin 22.
```
Optionally, you can initialize the strip with a set brightness (Defaults to ```0.1```):
```
example_strip_2 = WS2812(num_leds=10, pin_num=3, brightness=0.7)
```
Additionally, you can optionally set the random number generator the controller uses (```Callable[int, int]```) (Defaults to ```random.randInt```):
```
example_strip_3 = WS2812(num_leds=20, pin_num=6, random_generator=(YOUR OWN RANDOM GENERATOR))
```
However, you can change the number generator later utilizing the ```change_number_generator``` function.

# Functions
This controller offers various functions to interface with the light strip, controlling everything from the 

### Notes on Color
Please note that ```color``` values are int tuples, with each int representing the value for the Red, Green, and Blue of a pixel respectively (```(red,green,blue)```). These range between 0 and 255, however it will loop with higher values. Please note that brightness values are a float between 0 and 1. (i.e. ```RED = (255,0,0)``` and ```GREEN = (0,255,0)```).

### Notes on Brightness
The amount of brightness for a pixel is represented by a float between ```0.0``` and ```1.0```.

Additionally, please also note that for the random brightness functions, ```minB``` and ```maxB``` are both optional parameters which can restrict the range for the brightness.

## Update

First, let's start with perhaps the most important function you'll be using with this controller:
```
update() # Updates the state of the light strip
```
If you want any changes that you've made to the strip's state to show on the light strip, you'll need to call the ```update()``` function! No function within the controller will update the light strip automatically, you must do this manually.

## Pixel Operations
```
set_pixel_color(i, color) # Sets the color of the ith pixel to the given color
set_pixel_off(i) # Turns the ith pixel off
set_pixel_brightness(i, brightness) # Sets the ith pixel to the given brightness
set_pixel_brightness_random(i, minB, maxB) # Sets the ith pixel to a random brightness between minB and maxB
set_pixel_random(i) # Sets the given pixel to a random color
```

## Full Strip Operations
```
set_all(color) # Sets all pixels on the light strip to the same provided color
set_all_off() # Turns all lights in the light strip off
set_all_random_color() # Sets all pixels to a unified random color
set_all_brightness(brightness) # Sets all lights to a random brightness
set_all_brightness_random(brightness, minB, maxB) # Sets all lights to a random brightness between minB and maxB
set_all_brightness_random_solid(brightness, minB, maxB) # Sets all lights to a unified random brightness between minB and maxB
set_all_random() # Sets all pixels to a random color
```

## Section Operations
Section in this context means a section of the strip of lights (i.e. lights 3 through 6 would be a "section" of the strip).
```
set_section(colors[color | None], index) # Sets the section at index to the given array of colors, with None values indicating a random color
set_section_off(length, index) # Turns off the given section
set_section_solid(color, length, index) # Sets the section to the given color
set_section_brightness(brightness, length, index) # Sets the brightness of the given section
set_section_brightness_random(brightness, length, index, minB, maxB) # Sets all lights in a section to a random brightness between minB and maxB
set_section_brightness_random_solid(brightness, length, index, minB, maxB) # Sets all lights in a section to a unified random brightness between minB and maxB
set_section_random(length, index) # Fills the length long section at the index with random pixel colors
set_section_random_solid(length, index) # Sets the length long section to a unified random color
```
Please note that for these functions, ```index``` is an optional parameter, and will default to ```0``` (i.e. the section will start at the first light in the strip).

## Misc
```
get_pixel_color(i) -> color # Returns the color of the ith pixel
get_pixel_on(i) -> bool # Returns True if the pixel is on, false otherwise
get_pixel_brightness(i) -> float # Returns the brightness of the ith pixel
change_number_generator(random_generator) # Changes the internal random number generator of the controller (Callable(int, int))
```