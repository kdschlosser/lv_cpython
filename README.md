![image info](./assets/logo_text.png) 

____________________________

CPython bindings to the LVGL graphics framework.

LVGL originally was purpose built for rendering GUI controls on a touch 
interface attached to a micro controller. Over the yaars it has become a more 
complex frame work and caan be run over Javascript. LVGL has also had a binding 
created so it is able to run on MicroPython. Because of this progression it 
only makes sense to have a way to run it on a PC using CPython. That is what 
this binding does.

This binding uses CFFI to generate the C code needed to be able to compile
LVGL into an extension module that is able to be imported in Python. CFFI is 
not user friendly and it would require a person to have knowledge of the C 
programming language in order to use it. The build program creates wrappers
around all of the CFFI related bits to make it easier to use. No knowlegde of 
C is needed to be able to use this library.

There are are a few requirements in order to compile the library if a user so 
chooses to do so. There are wheels available for Windows 10+ running Python 
3.9, 3.10 or 3.11. There are also wheels available for OSX running Python 
3.9 and 3.10. To use the wheel for OSX you need to install SDL2. SDL2 is
cross platform software that provides a window to be able to render to. 
To install SDL2 you need to open a terminal and type in the following command
`brew install sdl2`. SDL2 is included in the Windows wheel. Linux folks are 
going to have to compile it if they want to install it. GCC is needed along 
with c11 standard libraries and SDL2.

To install using a wheel or for the linux folks to compile and install use 
the command `pip install lvgl` 


What can it be used for
------------------------

- ***MCU Development***: Having this library eliminates the compile/flash/test over and over again 
during the development cycle. you are able to develop a GUI in a much shorter 
time frame because of the elimination of having to compile and flash. you can 
simply run the code.


- ***Desktop use***: It can be used in combination with your favorite  Python GUI framework or it 
can also be used by itself. 
  <br/><br/>
  On Microsoft Windows PC's you can use LVGL to create OSD type graphics 
that have transparent backgrounds and no title bars, menus and window frames.


- ***Over the Internet***: It can also be used as a server side graphics framework over javascript. the 
frame buffer data can easily be sent over a socket connection and be rendered 
using javascript on a clients computer.



How to use
----------

If you are familiar with LVGL then you will be glad to know there aare 2 API's
available to this binding. One is the C style API and the other is the MicroPython
style. This is important to haave becaause the main goal of this library is to 
make development easier. The C API is for the users that want to use C code on 
their microcontroller and the MicroPython API is for the folks that want to 
run MicroPython.

the C API is whaat is activated by default and doing a simple `import lvgl as lv`
Is all that need to be done to use the C API. If you want to use the MicroPython
API then you would code the import `import lvgl.mpy as lv`.

There is special code that has to be used to aactivate the "display" and also 
to update LVGL. After you import LVGL the following code needs to be added.

```python
import lvgl as lv

DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

lv.init()
disp = lv.sdl_window_create(DISPLAY_WIDTH, DISPLAY_HEIGHT)
mouse = lv.sdl_mouse_create()
keyboard = lv.sdl_keyboard_create()
```

you can change the `DISPLAY_WIDTH` and `DISPLAY_HEIGHT` variables to whatever 
you want to use.

That takes care of setting up the display. Now to get LVGL to update and also
to keep the prograam running this is the "main loop" of the prograam. This has 
to be placed aat the very end of your code.

```python
import time  # NOQA

start = time.time()
    
while True:
    stop = time.time()
    diff = int((stop * 1000) - (start * 1000))
    if diff >= 1:
        start = stop
        lv.tick_inc(diff)
        lv.task_handler()
```

The code above is identical for both APIs. It also has to be removed before 
flashing if using the MicroPython API and beforer porting if using the C API.


check out the examples folder to see how the C API is used. For MicroPython 
there are examples in the documentation for LVGL.
